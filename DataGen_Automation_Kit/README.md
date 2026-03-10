# DataGen + Power Automate Upload Kit

This kit supports **two goals**:

1. **One-time generation** of import-ready CSV data using Copilot:
   - Customer
   - Vendor
   - Historical Sales Order / Invoice / Purchase Order
   - Current templates are included so you can generate current too if needed.

2. **Ongoing automation** (Power Automate) to upload:
   - Sales Orders **daily**
   - Purchase Orders **weekly** (or twice per week)

---

## Part 1 — One-time Copilot CSV generation

### 1) Setup (VS Code)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Generate Copilot prompts
```bash
python src/main.py generate-prompts
```

Prompts are written to `/prompts`.

### 3) Use Copilot
Open a prompt file (example: `prompts/Customer_prompt.txt`), paste into Copilot, then copy the CSV output into:

- `output/Customer.csv`
- `output/Vendor.csv`
- `output/SalesOrder_Historical.csv`
- `output/Invoice_Historical.csv`
- `output/PurchaseOrder_Historical.csv`

> Important: Copilot must output **CSV only** (no commentary).

### 4) Validate
```bash
python src/main.py validate
```

If validation fails, fix the CSV or regenerate with Copilot using the error messages.

---

## Part 2 — Power Automate for daily/weekly uploads

See:
- `power_automate/PowerAutomate_Upload_Blueprint.md`
- `power_automate/Payload_Mapping_Template.md`

You will need your API details (base URL + auth + payload shape). Once you fill those in, you can implement:
- Sales Orders upload flow (daily)
- Purchase Orders upload flow (weekly or 2x weekly)

---

## Templates included

- `templates/CustomerTemplate.csv`
- `templates/VendorTemplate.csv`
- `templates/SalesOrder_Historical.csv`
- `templates/Invoice_Historical.xlsx`
- `templates/PurchaseOrder_Historical.csv`
- `templates/SalesOrder_Current.csv`
- `templates/Invoice_Current.csv`
- `templates/PurchaseOrder_Current.csv`
