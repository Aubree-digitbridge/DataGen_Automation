from __future__ import annotations

import csv
import os
import random
import re
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROMPT_FILE = BASE / "prompts" / "salesOrder_daily_w_all_customerType_prompt.md"

TEMPLATE_FILE = BASE / "templates" / "SalesOrder_Current.csv"
CUSTOMER_FILE = BASE / "data" / "Customer_source.csv"
MAPPING_FILE = BASE / "data" / "Customer-Channel-ChannelAccountMapping.csv"

# Detailed product data with pricing/MSRP; used to enrich the SKU pool
SKU_FILES = [
    BASE / "data" / "Shoe-Products.csv",
    BASE / "data" / "Product_Vibes_PJ.csv",
    BASE / "data" / "Product_Vibes_SP.csv",
    BASE / "data" / "Product_Vibes_SP2.csv",
]

# Single authoritative SKU pool per prompt rules
SINGLE_SKU_FILE = BASE / "data" / "SKU_Only.csv"


def d2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append({(k or "").strip(): (v or "").strip() for k, v in row.items()})
        return rows


def load_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [h.strip() for h in next(csv.reader(f))]


def parse_decimal(value: str, default: Decimal = Decimal("0")) -> Decimal:
    try:
        cleaned = (value or "").strip().replace("$", "")
        if cleaned == "":
            return default
        return Decimal(cleaned)
    except Exception:
        return default


def load_prompt_config(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")

    def pick(pattern: str, default: str):
        m = re.search(pattern, text, flags=re.IGNORECASE)
        return m.group(1).strip() if m else default

    simulated_today = os.environ.get("SIMULATED_TODAY", "").strip()
    if simulated_today:
        today = date.fromisoformat(simulated_today)
    else:
        today = date.today()
    if "Use today's date to determine StartDate and EndDate".lower() in text.lower():
        if today.weekday() in (1, 2, 3, 4):
            start_date = today
            end_date = today
        elif today.weekday() == 0:
            start_date = today - timedelta(days=2)
            end_date = today
        else:
            start_date = today
            end_date = today
    else:
        start_date = date.fromisoformat(pick(r"StartDate\s*=\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", today.isoformat()))
        end_date = date.fromisoformat(pick(r"EndDate\s*=\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", today.isoformat()))

    def norm(v: str) -> str:
        v = v.strip()
        if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
            v = v[1:-1]
        if v in {"''", '""'}:
            return ""
        return v

    cfg = {
        "START_DATE": start_date,
        "END_DATE": end_date,
        "ORDERS_PER_DAY": int(pick(r"OrdersToGenerate\s*=\s*(\d+)", "20")),
        "SEQUENCE_START": int(pick(r"SequenceNumberStart\s*=\s*(\d+)", "1")),
        "MIN_QTY": int(pick(r"MinOrderQtyPerLine\s*=\s*(\d+)", "1")),
        "MAX_QTY": int(pick(r"MaxOrderQtyPerLine\s*=\s*(\d+)", "4")),
        "MIN_STYLES": int(pick(r"MinStylesPerOrder\s*=\s*(\d+)", "1")),
        "MAX_STYLES": int(pick(r"MaxStylesPerOrder\s*=\s*(\d+)", "3")),
        "MIN_TOTAL": Decimal(pick(r"MinOrderTotalAmount\s*=\s*(\d+(?:\.\d+)?)", "45")),
        "MAX_TOTAL": Decimal(pick(r"MaxOrderTotalAmount\s*=\s*(\d+(?:\.\d+)?)", "150")),
        "ORDER_TYPE": norm(pick(r"OrderType\s*=\s*([^\r\n]+)", "1")),
        "ORDER_STATUS": norm(pick(r"OrderStatus\s*=\s*([^\r\n]+)", "0")),
        "CURRENCY": norm(pick(r"Currency\s*=\s*([^\r\n]+)", "USD")),
        "UOM": norm(pick(r"UOM\s*=\s*([^\r\n]+)", "EA")),
        "STOCKABLE": norm(pick(r"Stockable\s*=\s*([^\r\n]+)", "TRUE")),
        "COSTABLE": norm(pick(r"Costable\s*=\s*([^\r\n]+)", "TRUE")),
        "TAXABLE": norm(pick(r"Taxable\s*=\s*([^\r\n]+)", "TRUE")),
        "IS_PROFIT": norm(pick(r"IsProfit\s*=\s*([^\r\n]+)", "TRUE")),
        "SHIP_QTY": norm(pick(r"ShipQty\s*=\s*([^\r\n]+)", "0")),
        "OPEN_QTY": norm(pick(r"OpenQty\s*=\s*([^\r\n]+)", "OrderQty")),
        "FINANCIAL_STATUS": norm(pick(r"Financial\s+Status\s*=\s*([^\r\n]+)", "")),
        "FULFILLMENT_STATUS": norm(pick(r"Fulfillment\s+Status\s*=\s*([^\r\n]+)", "")),
        "PAID_AMOUNT": norm(pick(r"PaidAmount\s*=\s*([^\r\n]+)", "0")),
        "BALANCE": norm(pick(r"Balance\s*=\s*([^\r\n]+)", "TotalAmount")),
    }

    cfg["DATE_LIST"] = [cfg["START_DATE"] + timedelta(days=i) for i in range((cfg["END_DATE"] - cfg["START_DATE"]).days + 1)]
    cfg["TOTAL_ORDERS"] = cfg["ORDERS_PER_DAY"] * len(cfg["DATE_LIST"])
    cfg["OUTPUT_FILE"] = BASE / "output" / f"SalesOrder_daily_w_all_customerType_{cfg['START_DATE'].strftime('%Y%m%d')}.csv"
    return cfg


def load_customers() -> list[dict]:
    # Customer_source.csv is pipe-delimited ("|") rather than comma-delimited.
    with CUSTOMER_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="|")
        rows = []
        for row in reader:
            rows.append({(k or "").strip(): (v or "").strip() for k, v in row.items()})
    mappings = read_csv_rows(MAPPING_FILE)

    map_by_code: dict[str, dict[str, str]] = {}
    for m in mappings:
        code = m.get("Customer Code", "")
        if code:
            map_by_code[code] = {
                "ChannelNum": m.get("Channel Num", ""),
                "ChannelAccountNum": m.get("Channel Account Num", ""),
            }

    city_county = {
        "Los Angeles": "Los Angeles",
        "Irvine": "Orange",
        "San Diego": "San Diego",
        "San Jose": "Santa Clara",
        "San Francisco": "San Francisco",
    }

    customers = []
    for i, r in enumerate(rows):
        code = r.get("Customer #", "")
        name = r.get("Customer Name", "")

        if not code or not name:
            continue

        # Derive Ecommerce / Retail / Wholesale from the customer code prefix
        # per prompt: three customer types.
        if code.startswith("wh-"):
            ctype = "Wholesale"
        elif code.startswith("re-") or code in {"JCPenney", "Macys"}:
            ctype = "Retail"
        else:
            ctype = "Ecommerce"

        mapping = map_by_code.get(code, {"ChannelNum": f"90{i:03d}", "ChannelAccountNum": f"19{i:03d}"})

        contact1 = r.get(" Contact", "") or r.get("Contact", "")
        contact2 = r.get(" Contact2", "") or r.get("Contact2", "")

        # Fallback phone/email use primary fields from the file
        phone = r.get(" Phone1", "") or r.get("Phone1", "")
        email = r.get(" Email", "") or r.get("Email", "")

        bill_city = r.get(" BillCity", "") or r.get("BillCity", "")
        ship_city = r.get(" ShipCity", "") or r.get("ShipCity", "")
        bill_state = r.get(" BillState", "CA") or r.get("BillState", "CA")
        ship_state = r.get(" ShipState", "CA") or r.get("ShipState", "CA")

        customers.append(
            {
                "CustomerCode": code,
                "CustomerName": name,
                "Type": ctype,
                "ChannelNum": mapping.get("ChannelNum", ""),
                "ChannelAccountNum": mapping.get("ChannelAccountNum", ""),
                "Contact1": contact1,
                "Contact2": contact2,
                "Phone": phone,
                "Email": email,
                # Bill-to fields
                "BillName": r.get(" BillName", "") or r.get("BillName", "") or name,
                "BillCompany": r.get(" BillCompany", "") or r.get("BillCompany", "") or name,
                "BillAddressLine1": r.get(" BillAddressLine1", "") or r.get("BillAddressLine1", ""),
                "BillAddressLine2": r.get(" BillAddressLine2", "") or r.get("BillAddressLine2", ""),
                "BillCity": bill_city,
                "BillState": bill_state,
                "BillZip": r.get(" BillPostalCode", "") or r.get("BillPostalCode", ""),
                "BillCounty": r.get(" BillCounty", "") or r.get("BillCounty", "") or city_county.get(bill_city, ""),
                "BillCountry": r.get(" BillCountry", "") or r.get("BillCountry", "") or "USA",
                "BillEmail": r.get(" BillEmail", "") or r.get("BillEmail", "") or email,
                "BillDaytimePhone": r.get(" BillDaytimePhone", "")
                or r.get("BillDaytimePhone", "")
                or phone,
                "BillDescription": r.get(" BillDescription", "") or r.get("BillDescription", ""),
                # Ship-to fields
                "ShipName": r.get(" ShipName", "") or r.get("ShipName", "") or name,
                "ShipCompany": r.get(" ShipCompany", "") or r.get("ShipCompany", "") or name,
                "ShipAddressLine1": r.get(" ShipAddressLine1", "") or r.get("ShipAddressLine1", ""),
                "ShipAddressLine2": r.get(" ShipAddressLine2", "") or r.get("ShipAddressLine2", ""),
                "ShipCity": ship_city,
                "ShipState": ship_state,
                "ShipZip": r.get(" ShipPostalCode", "") or r.get("ShipPostalCode", ""),
                "ShipCounty": r.get(" ShipCounty", "")
                or r.get("ShipCounty", "")
                or city_county.get(ship_city, ""),
                "ShipCountry": r.get(" ShipCountry", "") or r.get("ShipCountry", "") or "USA",
                "ShipEmail": r.get(" ShipEmail", "") or r.get("ShipEmail", "") or email,
                "ShipDaytimePhone": r.get(" ShipDaytimePhone", "")
                or r.get("ShipDaytimePhone", "")
                or phone,
                "ShipDescription": r.get(" ShipDescription", "") or r.get("ShipDescription", ""),
                # Sales reps from original file if present
                "SalesRep": r.get(" SalesRep", "") or r.get("SalesRep", ""),
                "SalesRep2": r.get(" SalesRep2", "") or r.get("SalesRep2", ""),
            }
        )

    if not customers:
        raise RuntimeError("No customers loaded from data/Customer_source.csv")
    return customers


def load_skus() -> list[dict]:
    # Per prompt, the authoritative SKU pool is SKU_Only.csv.
    # We enrich those SKUs with pricing/MSRP from the detailed product files.
    allowed_rows = read_csv_rows(SINGLE_SKU_FILE)
    allowed_skus = {r.get("SKU", "").strip() for r in allowed_rows if r.get("SKU", "").strip()}

    if not allowed_skus:
        raise RuntimeError("No SKU rows found in data/SKU_Only.csv")

    product_index: dict[str, dict[str, str]] = {}
    for p in SKU_FILES:
        for r in read_csv_rows(p):
            sku = (r.get("SKU", "") or "").strip()
            if not sku or sku not in allowed_skus:
                continue
            product_index[sku] = r

    result: list[dict] = []
    for sku in sorted(allowed_skus):
        meta = product_index.get(sku, {})
        wsp = parse_decimal(meta.get("Price", ""), Decimal("0"))
        msrp = parse_decimal(meta.get("MSRP", ""), Decimal("0"))

        # If we have no pricing metadata, fall back to a reasonable MSRP so that
        # Retail/Wholesale rules can still be satisfied.
        if msrp <= 0:
            msrp = Decimal("60")
        if wsp <= 0:
            wsp = d2(msrp * Decimal("0.6"))

        result.append(
            {
                "SKU": sku,
                "SKUTitle": meta.get("ProductTitle", ""),
                "WSP": wsp,
                "MSRP": msrp,
            }
        )

    if not result:
        raise RuntimeError("No SKU source rows found that match SKU_Only.csv")
    return result


def choose_customer_pool(customers: list[dict], order_date: date) -> list[dict]:
    weekday = order_date.weekday()
    pool = [c for c in customers if c["Type"] == "Ecommerce"]
    if weekday == 0:
        pool.extend([c for c in customers if c["Type"] == "Retail"])
    if weekday == 2:
        pool.extend([c for c in customers if c["Type"] == "Wholesale"])
    return pool if pool else customers


def make_lines_for_type(rng: random.Random, cfg: dict, customer_type: str, sku_pool: list[dict], shipping: Decimal):
    multiplier = 1
    price_mode = "ecom"
    if customer_type == "Retail":
        multiplier = 2
        price_mode = "retail"
    elif customer_type == "Wholesale":
        multiplier = 4
        price_mode = "wholesale"

    min_total = cfg["MIN_TOTAL"] * multiplier
    max_total = cfg["MAX_TOTAL"] * multiplier

    attempts = 0
    while attempts < 1200:
        attempts += 1

        styles = rng.randint(cfg["MIN_STYLES"], cfg["MAX_STYLES"])
        skus = rng.sample(sku_pool, k=styles)

        base_qtys = [rng.randint(cfg["MIN_QTY"], cfg["MAX_QTY"]) for _ in range(styles)]
        qtys = [q * multiplier for q in base_qtys]

        prices: list[Decimal] = []
        if price_mode == "ecom":
            prices = [d2(Decimal(rng.randint(1200, 8000)) / Decimal(100)) for _ in range(styles)]
        elif price_mode == "retail":
            valid = True
            for sku in skus:
                msrp = sku["MSRP"]
                if msrp <= 0:
                    valid = False
                    break
                prices.append(d2(msrp * Decimal("0.8")))
            if not valid:
                continue
        else:
            valid = True
            for sku in skus:
                wsp = sku["WSP"]
                if wsp <= 0:
                    valid = False
                    break
                prices.append(d2(wsp))
            if not valid:
                continue

        ext = [d2(Decimal(q) * p) for q, p in zip(qtys, prices)]
        sub_total = d2(sum(ext, Decimal("0")))
        total = d2(sub_total + shipping)

        if min_total <= total <= max_total:
            return skus, qtys, prices, ext, sub_total, total

    raise RuntimeError(f"Unable to create valid order lines for type={customer_type}")


def main():
    rng = random.Random(20260306)
    cfg = load_prompt_config(PROMPT_FILE)
    header = load_header(TEMPLATE_FILE)
    customers = load_customers()
    sku_pool = load_skus()

    rows = []
    per_type_count = defaultdict(int)

    for dt in cfg["DATE_LIST"]:
        customer_pool = choose_customer_pool(customers, dt)
        for seq in range(cfg["SEQUENCE_START"], cfg["SEQUENCE_START"] + cfg["ORDERS_PER_DAY"]):
            customer = rng.choice(customer_pool)
            ctype = customer["Type"]
            per_type_count[ctype] += 1

            order_number = f"{dt.strftime('%Y%m%d')}-{seq}"
            channel_order_id = f"{customer['ChannelNum']}-{dt.strftime('%y%m%d')}-{seq:06d}"

            shipping = d2(Decimal(rng.randint(0, 1800)) / Decimal(100)) if rng.random() < 0.9 else Decimal("0")
            skus, qtys, prices, exts, sub_total, total = make_lines_for_type(rng, cfg, ctype, sku_pool, shipping)

            ship_date = dt + timedelta(days=2)
            due_date = dt + timedelta(days=30)

            for idx in range(len(skus)):
                sku = skus[idx]
                qty = qtys[idx]
                price = prices[idx]
                ext = exts[idx]

                row = {k: "" for k in header}
                row["OrderNumber"] = order_number
                row["OrderType"] = cfg["ORDER_TYPE"]
                row["OrderStatus"] = cfg["ORDER_STATUS"]
                row["OrderDate"] = dt.isoformat()
                row["ShipDate"] = ship_date.isoformat()
                row["DueDate"] = due_date.isoformat()
                row["BillDate"] = dt.isoformat()

                row["CustomerCode"] = customer["CustomerCode"]
                row["CustomerName"] = customer["CustomerName"]
                row["Currency"] = cfg["CURRENCY"]
                row["SubTotalAmount"] = f"{sub_total:.2f}"
                row["TotalAmount"] = f"{total:.2f}"
                row["TaxRate"] = "0"
                row["TaxAmount"] = "0.00"
                row["DiscountRate"] = "0"
                row["DiscountAmount"] = "0.00"
                row["ShippingAmount"] = f"{shipping:.2f}"
                row["PaidAmount"] = f"{total:.2f}" if cfg["PAID_AMOUNT"].lower() == "totalamount" else cfg["PAID_AMOUNT"]
                row["Balance"] = f"{total:.2f}" if cfg["BALANCE"].lower() == "totalamount" else cfg["BALANCE"]

                row["SalesRep"] = customer.get("SalesRep", "")
                row["SalesRep2"] = customer.get("SalesRep2", "")
                row["Fulfillment Status"] = cfg["FULFILLMENT_STATUS"]
                row["Financial Status"] = cfg["FINANCIAL_STATUS"]

                row["ChannelNum"] = customer["ChannelNum"]
                row["ChannelAccountNum"] = customer["ChannelAccountNum"]
                row["ChannelOrderID"] = channel_order_id

                # Ship-to mapping per prompt rules (using customer source fields)
                row["ShipToName"] = customer["ShipName"]
                row["ShipToFirstName"] = customer["Contact1"]
                row["ShipToLastName"] = customer["Contact2"]
                row["ShipToCompany"] = customer["ShipCompany"]
                row["ShipToAddressLine1"] = customer["ShipAddressLine1"]
                row["ShipToAddressLine2"] = customer["ShipAddressLine2"]
                row["ShipToAddressLine3"] = customer["ShipDescription"]
                row["ShipToCity"] = customer["ShipCity"]
                row["ShipToState"] = customer["ShipState"]
                row["ShipToPostalCode"] = customer["ShipZip"]
                row["ShipToCounty"] = customer["ShipCounty"]
                row["ShipToCountry"] = customer["ShipCountry"]
                row["ShipToEmail"] = customer["ShipEmail"]
                row["ShipToDaytimePhone"] = customer["ShipDaytimePhone"]

                # Bill-to fields are required; copy from customer billing profile
                row["BillToName"] = customer["BillName"]
                row["BillToCompany"] = customer["BillCompany"]
                row["BillToAddressLine1"] = customer["BillAddressLine1"]
                row["BillToAddressLine2"] = customer["BillAddressLine2"]
                row["BillToAddressLine3"] = customer["BillDescription"]
                row["BillToCity"] = customer["BillCity"]
                row["BillToState"] = customer["BillState"]
                row["BillToPostalCode"] = customer["BillZip"]
                row["BillToCounty"] = customer["BillCounty"]
                row["BillToCountry"] = customer["BillCountry"]
                row["BillToEmail"] = customer["BillEmail"]
                row["BillToDaytimePhone"] = customer["BillDaytimePhone"]

                row["Seq"] = str(idx + 1)
                row["ItemDate"] = dt.isoformat()
                row["SKU"] = sku["SKU"]
                row["SKUTitle"] = sku["SKUTitle"]
                row["UOM"] = cfg["UOM"]

                row["OrderQty"] = str(qty)
                row["ShipQty"] = str(qty) if cfg["SHIP_QTY"].lower() == "orderqty" else cfg["SHIP_QTY"]
                row["CancelledQty"] = "0"
                row["OpenQty"] = str(qty) if cfg["OPEN_QTY"].lower() == "orderqty" else cfg["OPEN_QTY"]

                row["Price"] = f"{price:.2f}"
                row["ExtAmount"] = f"{ext:.2f}"
                row["ItemTotalAmount"] = f"{ext:.2f}"
                row["ShipAmount"] = "0.00"
                row["CancelledAmount"] = "0.00"
                row["OpenAmount"] = f"{ext:.2f}"

                row["Stockable"] = cfg["STOCKABLE"]
                row["Taxable"] = cfg["TAXABLE"]
                row["Costable"] = cfg["COSTABLE"]
                row["IsProfit"] = cfg["IS_PROFIT"]

                rows.append(row)

    output_file = cfg["OUTPUT_FILE"]
    with output_file.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(rows)

    def order_sort_key(order_id: str):
        if "-" in order_id:
            left, right = order_id.rsplit("-", 1)
            if left.isdigit() and right.isdigit():
                return (int(left), int(right))
        return (0, 0)

    unique_orders = sorted({r["OrderNumber"] for r in rows}, key=order_sort_key)
    next_seq = cfg["SEQUENCE_START"] + cfg["ORDERS_PER_DAY"]

    print("output_file", output_file.as_posix())
    print("rows", len(rows))
    print("unique_orders", len(unique_orders))
    print("orders_per_day", cfg["ORDERS_PER_DAY"])
    print("date_range_days", len(cfg["DATE_LIST"]))
    print("total_orders_expected", cfg["TOTAL_ORDERS"])
    print("order_number_min_max", unique_orders[0] if unique_orders else "", unique_orders[-1] if unique_orders else "")
    print("type_order_counts", dict(per_type_count))
    print("SequenceNumberStart", next_seq)


if __name__ == "__main__":
    main()
