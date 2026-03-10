from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT_FILE = BASE / "output" / f"Customer_w_allType_{date.today().strftime('%Y%m%d')}.csv"

HEADER = [
    "CustomerCode", "CustomerName", "Contact", "Contact2", "Contact3", "Phone1", "Phone2", "Phone3", "Phone4", "Email", "WebSite", "FirstDate", "Currency", "CreditLimit", "DiscountRate", "Area", "Region", "Terms", "TermsDays", "SalesRep", "SalesRep2", "CommissionRate", "CommissionRate2", "BillName", "BillCompany", "BillAddressLine1", "BillAddressLine2", "BillCity", "BillState", "BillPostalCode", "BillCounty", "BillCountry", "BillEmail", "BillDaytimePhone", "BillDescription", "ShipName", "ShipCompany", "ShipAddressLine1", "ShipAddressLine2", "ShipCity", "ShipState", "ShipPostalCode", "ShipCounty", "ShipCountry", "ShipEmail", "ShipDaytimePhone", "ShipDescription"
]

CITY_META = {
    "Los Angeles": {"area": "213", "prefix": "310", "county": "Los Angeles", "zip_start": 90001},
    "Irvine": {"area": "949", "prefix": "418", "county": "Orange", "zip_start": 92602},
    "San Diego": {"area": "619", "prefix": "278", "county": "San Diego", "zip_start": 92101},
    "San Jose": {"area": "408", "prefix": "662", "county": "Santa Clara", "zip_start": 95110},
    "San Francisco": {"area": "415", "prefix": "794", "county": "San Francisco", "zip_start": 94102},
}
CITIES = list(CITY_META.keys())

TERMS = [("Net30", "30"), ("Net45", "45"), ("Net60", "60")]
DISCOUNT_VALUES = ["0", "0.02", "0.05", "0.08", "0.10"]
SALES_REPS = ["Sam Lee", "Rina Patel", "Chris Wong", "Jordan Kim"]

ECOMM_CODES = [
    "eComm-AMZ-eCom",
    "eComm-Veeqo-Amazon",
    "eComm-eBay",
    "eComm-Etsy-LS",
    "eComm-Etsy-VS",
    "eComm-JCPenney",
    "eComm-Mirakl-Kohls",
    "eComm-Macys",
    "eComm-Magento",
    "eComm-Shopify",
    "eComm-Squarespace",
    "eComm-Tiktok",
    "eComm-Walmart-eComm",
]

WHOLESALE_NAMES = [
    "Golden State Apparel",
    "Pacific Ridge Outfitters",
    "Harbor West Collective",
]

RETAIL_NAMES = [
    "Sunset Avenue Boutique",
    "Coastal Bloom Studio",
]

NORMAL_NAMES = [
    "Northbay Garments Co",
    "Blue Harbor Trading",
    "Canyon Peak Supply",
    "Redwood Lane Brands",
    "Metro Valley Distributors",
    "Silver Oak Textiles",
    "Urban Crest Commerce",
    "Mission Trail Outfitters",
    "Summit Grove Partners",
    "Ocean Park Goods",
    "Golden Gate Retail Group",
    "Santa Clara Apparel House",
    "Sierra Vista Merchants",
    "Bayline Fashion Works",
    "Pacific Union Clothiers",
]

FIRST_NAMES = [
    "Aiden", "Bella", "Caleb", "Diana", "Ethan", "Fiona", "Gavin", "Holly", "Isaac", "Julia",
    "Kevin", "Lila", "Mason", "Nora", "Owen", "Paige", "Quinn", "Riley", "Sophia", "Tyler",
    "Uma", "Victor", "Willow", "Xavier", "Yara", "Zane", "Amelia", "Brandon", "Carmen", "Dominic",
    "Elena", "Felix", "Gianna", "Henry", "Ivy", "Jonah", "Kara", "Landon", "Mila", "Noah",
    "Olivia", "Preston", "Rosa", "Sebastian", "Tara", "Uri", "Valerie", "Wesley", "Yvette", "Zelda",
    "Aria", "Blake", "Cora", "Derek", "Ember", "Frank", "Grace", "Harper", "Ian", "Jade"
]

LAST_NAMES = [
    "Adams", "Bennett", "Carter", "Diaz", "Evans", "Foster", "Garcia", "Hayes", "Irwin", "Jordan",
    "Keller", "Lopez", "Mitchell", "Nelson", "Owens", "Parker", "Quincy", "Reed", "Sullivan", "Turner",
    "Underwood", "Vargas", "Walker", "Xu", "Young", "Zimmer", "Anderson", "Brooks", "Coleman", "Dawson",
    "Edwards", "Fleming", "Gibson", "Hughes", "Ingram", "James", "Knight", "Lawson", "Morris", "Nash",
    "Ortega", "Pierce", "Quinn", "Ramirez", "Sanders", "Thomas", "Usher", "Vance", "White", "Yates",
    "Abbott", "Bryant", "Conner", "Dalton", "Ellis", "Flynn", "Griffin", "Horton", "Iverson", "Jennings"
]


def make_code(prefix: str, name: str) -> str:
    parts = [x for x in name.replace("&", " ").replace("-", " ").split() if x]
    first = parts[0]
    rest = "".join(p[0].upper() for p in parts[1:])
    return f"{prefix}-{first}-{rest}" if rest else f"{prefix}-{first}"


def phone(area: str, prefix: str, seq: int) -> str:
    return f"({area}) {prefix}-{seq:04d}"


def first_date(i: int) -> str:
    start = date(2024, 1, 15)
    return (start + timedelta(days=i % 20)).isoformat()


def build_rows() -> list[list[str]]:
    all_specs: list[tuple[str, str, str]] = []

    for code in ECOMM_CODES:
        display = code.replace("eComm-", "").replace("-", " ")
        all_specs.append(("ec", display, code))

    all_specs.extend(("wh", n, make_code("wh", n)) for n in WHOLESALE_NAMES)
    all_specs.extend(("re", n, make_code("re", n)) for n in RETAIL_NAMES)
    all_specs.extend(("cu", n, make_code("cu", n)) for n in NORMAL_NAMES)

    all_specs = all_specs[:20]

    rows: list[list[str]] = []
    phone_seed = 1000

    for i, (kind, name, customer_code) in enumerate(all_specs):
        city = CITIES[i % len(CITIES)]
        city_info = CITY_META[city]
        area = city_info["area"]
        prefix = city_info["prefix"]
        county = city_info["county"]
        postal = str(city_info["zip_start"] + i)

        terms, terms_days = TERMS[i % len(TERMS)]
        discount = DISCOUNT_VALUES[i % len(DISCOUNT_VALUES)]

        sales_rep = SALES_REPS[i % len(SALES_REPS)]
        sales_rep2 = SALES_REPS[(i + 1) % len(SALES_REPS)]

        contact = f"{FIRST_NAMES[(i * 3) % len(FIRST_NAMES)]} {LAST_NAMES[(i * 3) % len(LAST_NAMES)]}"
        contact2 = f"{FIRST_NAMES[(i * 3 + 1) % len(FIRST_NAMES)]} {LAST_NAMES[(i * 3 + 1) % len(LAST_NAMES)]}"
        contact3 = f"{FIRST_NAMES[(i * 3 + 2) % len(FIRST_NAMES)]} {LAST_NAMES[(i * 3 + 2) % len(LAST_NAMES)]}"

        email_slug = customer_code.lower().replace(" ", "-")
        email = f"{email_slug}@customers.example.com"
        website = f"www.{email_slug}.example.com"

        bill_addr1 = f"{100 + i} Market St"
        bill_addr2 = f"Suite {100 + i}"
        ship_addr1 = f"{200 + i} Harbor Ave"
        ship_addr2 = f"Dock {i % 9 + 1}"

        credit_limit = f"{15000 + i * 4500:.2f}"
        com1 = f"{(i % 9) / 100:.2f}"
        com2 = f"{((i + 3) % 9) / 100:.2f}"

        p1 = phone(area, prefix, phone_seed)
        p2 = phone(area, prefix, phone_seed + 1)
        p3 = phone(area, prefix, phone_seed + 2)
        p4 = phone(area, prefix, phone_seed + 3)
        p_bill = phone(area, prefix, phone_seed + 4)
        p_ship = phone(area, prefix, phone_seed + 5)
        phone_seed += 6

        row = [
            customer_code,
            name,
            contact,
            contact2,
            contact3,
            p1,
            p2,
            p3,
            p4,
            email,
            website,
            first_date(i),
            "USD",
            credit_limit,
            discount,
            "West",
            "CA",
            terms,
            terms_days,
            sales_rep,
            sales_rep2,
            com1,
            com2,
            f"{name} Billing",
            name,
            bill_addr1,
            bill_addr2,
            city,
            "CA",
            postal,
            county,
            "USA",
            f"billing-{email_slug}@example.com",
            p_bill,
            "Primary billing profile",
            f"{name} Shipping",
            name,
            ship_addr1,
            ship_addr2,
            city,
            "CA",
            str(int(postal) + 200),
            county,
            "USA",
            f"ship-{email_slug}@example.com",
            p_ship,
            "Primary shipping profile",
        ]

        rows.append(row)

    return rows


def main():
    rows = build_rows()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUT_FILE.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)

    print("output_file", OUT_FILE.as_posix())
    print("rows", len(rows))


if __name__ == "__main__":
    main()
