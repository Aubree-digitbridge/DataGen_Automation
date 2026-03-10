# Payload Mapping Template (fill in once)

Use this to map your CSV/template columns to the API JSON payload.

---

## Sales Order API

### Endpoint
- POST: {{SALES_ORDER_ENDPOINT}}
- Accepts: (choose)
  - [ ] single order per request
  - [ ] bulk array of orders

### Payload shape (example — header + lines)
```json
{
  "orderNumber": "SO-2026-000123",
  "orderDate": "2026-03-02",
  "customerCode": "CUST-000045",
  "currency": "USD",
  "status": "Open",
  "shipTo": {
    "name": "John Smith",
    "address1": "123 Main St",
    "city": "Monrovia",
    "state": "CA",
    "zip": "91016",
    "country": "US"
  },
  "lines": [
    {
      "sku": "SKU-001",
      "qty": 2,
      "unitPrice": 19.99,
      "discount": 0.00
    }
  ]
}
```

### Field mapping table (fill in)
- orderNumber  <- CSV column: ___________________
- orderDate    <- CSV column: ___________________
- customerCode <- CSV column: ___________________
- status       <- CSV column: ___________________
- lines[].sku  <- CSV column: ___________________
- lines[].qty  <- CSV column: ___________________
- lines[].unitPrice <- CSV column: ___________________

---

## Purchase Order API

### Endpoint
- POST: {{PURCHASE_ORDER_ENDPOINT}}

### Payload shape (example)
```json
{
  "poNumber": "PO-2026-000055",
  "poDate": "2026-03-02",
  "vendorCode": "VEND-000012",
  "status": "Open",
  "lines": [
    {
      "sku": "SKU-001",
      "qty": 10,
      "unitCost": 8.50
    }
  ]
}
```

### Field mapping table (fill in)
- poNumber   <- CSV column: ___________________
- poDate     <- CSV column: ___________________
- vendorCode <- CSV column: ___________________
- lines[].sku <- CSV column: ___________________
- lines[].qty <- CSV column: ___________________
- lines[].unitCost <- CSV column: ___________________

---

## Notes for Power Automate
- Use **Select** to map rows into JSON.
- If header+lines needed, group by orderNumber/poNumber, then build `lines` array.
