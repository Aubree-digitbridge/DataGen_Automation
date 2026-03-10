from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from collections import defaultdict
import re

BASE = Path(__file__).resolve().parents[1]
PROMPT_FILE = BASE / "prompts" / "SalesOrder_daily_prompt.md"
if not PROMPT_FILE.exists():
    PROMPT_FILE = BASE / "prompts" / "SalesOrder_daily_prompt.txt"

TEMPLATE_FILE = BASE / "templates" / "SalesOrder_Current.csv"
CUSTOMER_FILE = BASE / "output" / "Customer.csv"
MAPPING_FILE = BASE / "data" / "Customer-Channel-ChannelAccountMapping.csv"
SKU_FILES = [
    BASE / "data" / "Shoe-Products.csv",
    BASE / "data" / "Product_Vibes_PJ.csv",
    BASE / "data" / "Product_Vibes_SP.csv",
    BASE / "data" / "Product_Vibes_SP2.csv",
]
START_DATE = date(2026, 3, 5)
END_DATE = date(2026, 3, 5)
ORDERS_TO_GENERATE = 20

MIN_QTY = 1
MAX_QTY = 4
MIN_STYLES = 1
MAX_STYLES = 3
MIN_TOTAL = Decimal("45.00")
MAX_TOTAL = Decimal("150.00")


def load_prompt_parameters(path: Path):
    text = path.read_text(encoding="utf-8")

    def pick(pattern: str, default: str):
        m = re.search(pattern, text, flags=re.IGNORECASE)
        return m.group(1).strip() if m else default

    explicit_start = pick(r"StartDate\s*=\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", "")
    explicit_end = pick(r"EndDate\s*=\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", "")

    today = date.today()
    has_dynamic_date_rule = "Use today's date to determine StartDate and EndDate".lower() in text.lower()
    if has_dynamic_date_rule:
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
        start_date = date.fromisoformat(explicit_start or "2026-03-05")
        end_date = date.fromisoformat(explicit_end or "2026-03-05")

    sequence_start = int(pick(r"SequenceNumberStart\s*=\s*(\d+)", "1"))
    if "SequenceNumberStart" not in text:
        legacy_start = pick(r"OrderNumberStart\s*=\s*(\d+)", "1")
        sequence_start = int(legacy_start)

    cfg = {
        "START_DATE": start_date,
        "END_DATE": end_date,
        "ORDERS_PER_DAY": int(pick(r"OrdersToGenerate\s*=\s*(\d+)", "20")),
        "SEQUENCE_START": sequence_start,
        "MIN_QTY": int(pick(r"MinOrderQtyPerLine\s*=\s*(\d+)", "1")),
        "MAX_QTY": int(pick(r"MaxOrderQtyPerLine\s*=\s*(\d+)", "4")),
        "MIN_STYLES": int(pick(r"MinStylesPerOrder\s*=\s*(\d+)", "1")),
        "MAX_STYLES": int(pick(r"MaxStylesPerOrder\s*=\s*(\d+)", "3")),
        "MIN_TOTAL": Decimal(pick(r"MinOrderTotalAmount\s*=\s*(\d+(?:\.\d+)?)", "45")),
        "MAX_TOTAL": Decimal(pick(r"MaxOrderTotalAmount\s*=\s*(\d+(?:\.\d+)?)", "150")),
        "ORDER_TYPE": pick(r"OrderType\s*=\s*([^\r\n]+)", "1"),
        "ORDER_STATUS": pick(r"OrderStatus\s*=\s*([^\r\n]+)", "0"),
        "CURRENCY": pick(r"Currency\s*=\s*([^\r\n]+)", "USD"),
        "UOM": pick(r"UOM\s*=\s*([^\r\n]+)", "EA"),
        "STOCKABLE": pick(r"Stockable\s*=\s*([^\r\n]+)", "TRUE"),
        "COSTABLE": pick(r"Costable\s*=\s*([^\r\n]+)", "TRUE"),
        "TAXABLE": pick(r"Taxable\s*=\s*([^\r\n]+)", "TRUE"),
        "IS_PROFIT": pick(r"IsProfit\s*=\s*([^\r\n]+)", "TRUE"),
        "SHIP_QTY": pick(r"ShipQty\s*=\s*([^\r\n]+)", "0"),
        "OPEN_QTY": pick(r"OpenQty\s*=\s*([^\r\n]+)", "OrderQty"),
        "FINANCIAL_STATUS": pick(r"Financial\s+Status\s*=\s*([^\r\n]+)", "''"),
        "FULFILLMENT_STATUS": pick(r"Fulfillment\s+Status\s*=\s*([^\r\n]+)", "''"),
        "PAID_AMOUNT": pick(r"PaidAmount\s*=\s*([^\r\n]+)", "0"),
        "BALANCE": pick(r"Balance\s*=\s*([^\r\n]+)", "TotalAmount"),
    }

    def normalize_default(value: str) -> str:
        v = value.strip()
        if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
            v = v[1:-1]
        if v == "''" or v == '""':
            return ""
        return v

    for key in [
        "ORDER_TYPE",
        "ORDER_STATUS",
        "CURRENCY",
        "UOM",
        "STOCKABLE",
        "COSTABLE",
        "TAXABLE",
        "IS_PROFIT",
        "SHIP_QTY",
        "OPEN_QTY",
        "FINANCIAL_STATUS",
        "FULFILLMENT_STATUS",
        "PAID_AMOUNT",
        "BALANCE",
    ]:
        cfg[key] = normalize_default(str(cfg[key]))

    cfg["DATE_LIST"] = [cfg["START_DATE"] + timedelta(days=i) for i in range((cfg["END_DATE"] - cfg["START_DATE"]).days + 1)]
    cfg["TOTAL_ORDERS"] = cfg["ORDERS_PER_DAY"] * len(cfg["DATE_LIST"])
    cfg["OUTPUT_FILE"] = BASE / "output" / f"SalesOrder_daily_{cfg['START_DATE'].strftime('%Y%m%d')}.csv"
    return cfg


def d2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def read_csv_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        result = []
        for row in reader:
            cleaned = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            result.append(cleaned)
        return result


def load_header(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        return [h.strip() for h in next(reader)]


def load_customer_mapping():
    customers = read_csv_rows(CUSTOMER_FILE)
    mappings = read_csv_rows(MAPPING_FILE)

    customer_by_code = {r.get("CustomerCode", ""): r for r in customers if r.get("CustomerCode", "")}

    valid = []
    for row in mappings:
        customer_code = row.get("Customer Code", "")
        if customer_code in customer_by_code:
            valid.append(
                {
                    "CustomerCode": customer_code,
                    "CustomerName": customer_by_code[customer_code].get("CustomerName", ""),
                    "ChannelNum": row.get("Channel Num", ""),
                    "ChannelAccountNum": row.get("Channel Account Num", ""),
                    "customer": customer_by_code[customer_code],
                }
            )

    if not valid:
        raise RuntimeError("No valid customer/mapping rows found")

    return valid


def load_sku_pool():
    pool = []
    for path in SKU_FILES:
        for row in read_csv_rows(path):
            sku = row.get("SKU", "")
            if not sku:
                continue
            product_title = row.get("ProductTitle", "")
            pool.append({"SKU": sku, "SKUTitle": product_title})
    if not pool:
        raise RuntimeError("No SKUs found in source files")
    return pool


def choose_line_plan(rng: random.Random, shipping_amount: Decimal):
    attempts = 0
    while attempts < 1000:
        attempts += 1
        num_styles = rng.randint(CFG["MIN_STYLES"], CFG["MAX_STYLES"])
        qtys = [rng.randint(CFG["MIN_QTY"], CFG["MAX_QTY"]) for _ in range(num_styles)]

        min_sub = Decimal(sum(q * 12 for q in qtys))
        max_sub = Decimal(sum(q * 80 for q in qtys))

        target_sub_min = max(min_sub, CFG["MIN_TOTAL"] - shipping_amount)
        target_sub_max = min(max_sub, CFG["MAX_TOTAL"] - shipping_amount)

        if target_sub_min > target_sub_max:
            continue

        cents_min = int((target_sub_min * 100).to_integral_value())
        cents_max = int((target_sub_max * 100).to_integral_value())
        target_sub = Decimal(rng.randint(cents_min, cents_max)) / Decimal(100)

        prices = []
        running = Decimal("0")
        for q in qtys[:-1]:
            price = Decimal(rng.randint(1200, 8000)) / Decimal(100)
            price = d2(price)
            prices.append(price)
            running += Decimal(q) * price

        q_last = qtys[-1]
        p_last = d2((target_sub - running) / Decimal(q_last))
        if p_last < Decimal("12.00") or p_last > Decimal("80.00"):
            continue

        prices.append(p_last)

        ext_amounts = [d2(Decimal(q) * p) for q, p in zip(qtys, prices)]
        sub_total = d2(sum(ext_amounts, Decimal("0")))
        total = d2(sub_total + shipping_amount)

        if CFG["MIN_TOTAL"] <= total <= CFG["MAX_TOTAL"]:
            return qtys, prices, ext_amounts, sub_total, total

    raise RuntimeError("Failed to generate valid line plan")


def main():
    rng = random.Random(20260305)
    global CFG
    CFG = load_prompt_parameters(PROMPT_FILE)

    header = load_header(TEMPLATE_FILE)
    valid_customers = load_customer_mapping()
    sku_pool = load_sku_pool()

    order_dates = CFG["DATE_LIST"]
    if not order_dates:
        raise RuntimeError("Invalid date range")

    all_rows = []

    order_items = []
    for dt in order_dates:
        for seq in range(CFG["SEQUENCE_START"], CFG["SEQUENCE_START"] + CFG["ORDERS_PER_DAY"]):
            order_items.append((dt, seq))

    for order_idx, (order_date, sequence_number) in enumerate(order_items):
        order_number = f"{order_date.strftime('%Y%m%d')}-{sequence_number}"
        ship_date = order_date + timedelta(days=2)
        due_date = order_date + timedelta(days=30)

        customer = rng.choice(valid_customers)
        c = customer["customer"]
        channel_num = customer["ChannelNum"]
        channel_acct = customer["ChannelAccountNum"]

        channel_order_id = f"{channel_num}-{order_date.strftime('%y%m%d')}-{order_idx + 1:06d}"

        with_shipping = rng.random() < 0.90
        shipping_amount = d2(Decimal(rng.randint(0, 1800)) / Decimal(100)) if with_shipping else Decimal("0.00")

        qtys, prices, ext_amounts, sub_total, total = choose_line_plan(rng, shipping_amount)

        chosen_skus = rng.sample(sku_pool, k=len(qtys))

        for line_idx in range(len(qtys)):
            qty = qtys[line_idx]
            price = prices[line_idx]
            ext = ext_amounts[line_idx]
            sku = chosen_skus[line_idx]

            row = {k: "" for k in header}

            row["OrderNumber"] = str(order_number)
            row["OrderType"] = CFG["ORDER_TYPE"]
            row["OrderStatus"] = CFG["ORDER_STATUS"]
            row["OrderDate"] = order_date.isoformat()
            row["ShipDate"] = ship_date.isoformat()
            row["DueDate"] = due_date.isoformat()
            row["BillDate"] = order_date.isoformat()

            row["CustomerCode"] = customer["CustomerCode"]
            row["CustomerName"] = customer["CustomerName"]
            row["Currency"] = CFG["CURRENCY"]

            row["SubTotalAmount"] = f"{sub_total:.2f}"
            row["TotalAmount"] = f"{total:.2f}"
            row["TaxRate"] = "0"
            row["TaxAmount"] = "0.00"
            row["DiscountRate"] = "0"
            row["DiscountAmount"] = "0.00"
            row["ShippingAmount"] = f"{shipping_amount:.2f}"
            row["PaidAmount"] = f"{total:.2f}" if CFG["PAID_AMOUNT"].lower() == "totalamount" else CFG["PAID_AMOUNT"]
            row["Balance"] = f"{total:.2f}" if CFG["BALANCE"].lower() == "totalamount" else CFG["BALANCE"]

            row["Fulfillment Status"] = CFG["FULFILLMENT_STATUS"]
            row["Financial Status"] = CFG["FINANCIAL_STATUS"]

            row["ChannelNum"] = channel_num
            row["ChannelAccountNum"] = channel_acct
            row["ChannelOrderID"] = channel_order_id

            row["ShipToName"] = c.get("ShipName", "")
            row["ShipToFirstName"] = c.get("Contact", "")
            row["ShipToLastName"] = c.get("Contact2", "")
            row["ShipToCompany"] = c.get("ShipCompany", "")
            row["ShipToAddressLine1"] = c.get("ShipAddressLine1", "")
            row["ShipToAddressLine2"] = c.get("ShipAddressLine2", "")
            row["ShipToAddressLine3"] = c.get("ShipDescription", "")
            row["ShipToCity"] = c.get("ShipCity", "")
            row["ShipToState"] = c.get("ShipState", "")
            row["ShipToPostalCode"] = c.get("ShipPostalCode", "")
            row["ShipToCounty"] = c.get("ShipCounty", "")
            row["ShipToCountry"] = c.get("ShipCountry", "")
            row["ShipToEmail"] = c.get("ShipEmail", "")
            row["ShipToDaytimePhone"] = c.get("ShipDaytimePhone", "")

            row["BillToName"] = row["ShipToName"]
            row["BillToCompany"] = row["ShipToCompany"]
            row["BillToAddressLine1"] = row["ShipToAddressLine1"]
            row["BillToAddressLine2"] = row["ShipToAddressLine2"]
            row["BillToAddressLine3"] = row["ShipToAddressLine3"]
            row["BillToCity"] = row["ShipToCity"]
            row["BillToState"] = row["ShipToState"]
            row["BillToPostalCode"] = row["ShipToPostalCode"]
            row["BillToCounty"] = row["ShipToCounty"]
            row["BillToCountry"] = row["ShipToCountry"]
            row["BillToEmail"] = row["ShipToEmail"]
            row["BillToDaytimePhone"] = row["ShipToDaytimePhone"]

            row["Seq"] = str(line_idx + 1)
            row["ItemDate"] = order_date.isoformat()
            row["SKU"] = sku["SKU"]
            row["SKUTitle"] = sku["SKUTitle"]
            row["UOM"] = CFG["UOM"]

            row["OrderQty"] = str(qty)
            row["ShipQty"] = str(qty) if CFG["SHIP_QTY"].lower() == "orderqty" else CFG["SHIP_QTY"]
            row["CancelledQty"] = "0"
            row["OpenQty"] = str(qty) if CFG["OPEN_QTY"].lower() == "orderqty" else CFG["OPEN_QTY"]

            row["Price"] = f"{price:.2f}"
            row["ExtAmount"] = f"{ext:.2f}"
            row["ItemTotalAmount"] = f"{ext:.2f}"
            row["ShipAmount"] = "0.00"
            row["CancelledAmount"] = "0.00"
            row["OpenAmount"] = f"{ext:.2f}"

            row["Stockable"] = CFG["STOCKABLE"]
            row["Taxable"] = CFG["TAXABLE"]
            row["Costable"] = CFG["COSTABLE"]
            row["IsProfit"] = CFG["IS_PROFIT"]

            all_rows.append(row)

    output_file = CFG["OUTPUT_FILE"]
    try:
        with output_file.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(all_rows)
    except PermissionError:
        output_file = output_file.with_name(f"{output_file.stem}_rerun.csv")
        with output_file.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(all_rows)

    orders = defaultdict(list)
    for row in all_rows:
        orders[row["OrderNumber"]].append(row)

    day_counts = defaultdict(int)
    for order_num, lines in orders.items():
        day_counts[lines[0]["OrderDate"]] += 1

    max_per_day = max(day_counts.values()) if day_counts else 0
    totals_out_of_range = 0
    style_violations = 0
    qty_violations = 0
    for order_num, lines in orders.items():
        total = Decimal(lines[0]["TotalAmount"])
        if not (CFG["MIN_TOTAL"] <= total <= CFG["MAX_TOTAL"]):
            totals_out_of_range += 1
        skus = {line["SKU"] for line in lines if line["SKU"]}
        if not (CFG["MIN_STYLES"] <= len(skus) <= CFG["MAX_STYLES"]):
            style_violations += 1
        for line in lines:
            q = int(line["OrderQty"])
            if not (CFG["MIN_QTY"] <= q <= CFG["MAX_QTY"]):
                qty_violations += 1

    sequence_values = []
    for order_id in orders.keys():
        if "-" in order_id:
            tail = order_id.rsplit("-", 1)[1]
            if tail.isdigit():
                sequence_values.append(int(tail))
    last_sequence = max(sequence_values) if sequence_values else CFG["SEQUENCE_START"] - 1
    next_start = last_sequence + 1

    def order_sort_key(order_id: str):
        if "-" in order_id:
            day_part, seq_part = order_id.rsplit("-", 1)
            if day_part.isdigit() and seq_part.isdigit():
                return (int(day_part), int(seq_part))
        return (0, 0)

    order_id_sorted = sorted(orders.keys(), key=order_sort_key)
    first_order = order_id_sorted[0] if order_id_sorted else ""
    last_order = order_id_sorted[-1] if order_id_sorted else ""

    print("output_file", output_file.as_posix())
    print("rows", len(all_rows))
    print("unique_orders", len(orders))
    print("orders_per_day", CFG["ORDERS_PER_DAY"])
    print("date_range_days", len(order_dates))
    print("total_orders_expected", CFG["TOTAL_ORDERS"])
    print("order_number_min_max", first_order, last_order)
    print("max_orders_single_day", max_per_day)
    print("totals_out_of_range", totals_out_of_range)
    print("styles_out_of_range", style_violations)
    print("qty_out_of_range_rows", qty_violations)
    print("SequenceNumberStart", next_start)


if __name__ == "__main__":
    main()
