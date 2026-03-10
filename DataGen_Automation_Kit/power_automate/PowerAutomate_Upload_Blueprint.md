# Power Automate Upload Blueprint (Sales Order daily, Purchase Order weekly)

This doc is **implementation-ready** once you fill in your API details.

---

## 0) Recommended architecture

Create **two cloud flows**:

### Flow A — Upload Sales Orders (Daily)
- Trigger: **Recurrence** (Daily)
- Source: SQL / SharePoint List / Excel / CSV export (choose your true source)
- Transform: build JSON payloads (header + lines if needed)
- Send: HTTP POST to API
- Log + notify: store results and errors

### Flow B — Upload Purchase Orders (Weekly or 2x weekly)
- Trigger: **Recurrence** (Weekly or twice per week)
- Same pattern as Sales Order

---

## 1) Authentication patterns

Choose one:

### A) API Key
- Store the key in Power Automate as an **Environment Variable** (recommended) or as a secure input.
- HTTP header example:
  - `x-api-key: <your key>`

### B) OAuth2
- Recommended: **Custom Connector**
- Configure OAuth2 in connector so each HTTP action doesn’t need manual token logic.

### C) Token endpoint (username/password -> bearer token)
- Step 1: HTTP POST to `/auth/token`
- Step 2: Parse JSON token
- Step 3: Use `Authorization: Bearer <token>` in subsequent calls

---

## 2) Flow A — Sales Order daily (step-by-step)

### Trigger
- Action: Recurrence
- Frequency: Daily
- Time zone: America/Los_Angeles
- Time: e.g., 06:00

### Get new/changed records
Choose one:
- **SQL Server**: "Execute a SQL query" that returns orders created/updated since last run
- **SharePoint**: "Get items" with filter `Modified ge 'last_run'`
- **Excel**: "List rows present in a table"

Store last successful run time in:
- SharePoint list `Integration_RunLog` OR
- Dataverse table OR
- Azure Table (if you have it)

### Transform to payload
If your API accepts **bulk**:
- Use **Select** to map rows into JSON array

If your API requires **header + lines**:
- Use grouping by `OrderNumber`
- Build `lines` array per order (use variables + Append to array variable)

### Send to API
- Action: HTTP
- Method: POST
- Uri: `{{SALES_ORDER_ENDPOINT}}`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>` (or API key)
- Body: JSON

### Handle response
- If success:
  - Write run log record: count, status, response id(s)
- If failure:
  - Save payload to OneDrive/SharePoint as `SO_Failed_<timestamp>.json`
  - Log the error text
  - Send Teams/Email notification

### Idempotency / Duplicate prevention (highly recommended)
Use one of these:
- API supports `Idempotency-Key` header -> set to OrderNumber
- Or: call GET `/salesorders/{OrderNumber}` first; if exists, skip

---

## 3) Flow B — Purchase Order weekly / twice weekly

### Trigger options
Weekly once:
- Recurrence: Weekly
- Day: Monday
- Time: 06:15

Twice per week:
- Recurrence: Weekly
- Days: Monday + Thursday
- Time: 06:15

Then follow the same pattern as Sales Order:
- Get new POs since last run
- Transform payload
- POST to `{{PURCHASE_ORDER_ENDPOINT}}`
- Log + alert failures

---

## 4) Minimum logging table (SharePoint list suggestion)

Create SharePoint list: `Integration_RunLog`
Columns:
- FlowName (text)
- RunStart (datetime)
- RunEnd (datetime)
- RecordsAttempted (number)
- RecordsSucceeded (number)
- RecordsFailed (number)
- Status (choice: Success/Partial/Failed)
- ErrorSummary (multiple lines)
- PayloadFileLink (hyperlink)

---

## 5) What you need to fill in

- SALES_ORDER_ENDPOINT
- PURCHASE_ORDER_ENDPOINT
- Auth method (API key / OAuth / token endpoint)
- Payload JSON schema (flat rows vs header+lines)
- Source of daily data (SQL/Excel/SharePoint)
