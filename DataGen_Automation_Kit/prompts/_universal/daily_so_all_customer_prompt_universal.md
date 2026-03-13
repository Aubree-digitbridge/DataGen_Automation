You are generating import-ready CSV data.

STRICT RULES (do not violate)

Output CSV ONLY. No explanations, no markdown, no code fences.

The first line MUST be the header row EXACTLY as provided.

Do NOT add/remove/rename columns.

Every row must have the same number of columns as the header.

Do not include blank lines.

If a field contains commas, wrap that field in double quotes.

ENTITY: SalesOrder
DATASET TYPE: HISTORICAL (eCommerce realistic behavior)

================================================
HARDCODED HEADER (MUST MATCH EXACTLY)

The first CSV row must be this exact header, in this exact order:

OrderNumber
OrderType
OrderStatus
OrderDate
ShipDate
DueDate
BillDate
EtaArrivalDate
EarliestShipDate
LatestShipDate
SignatureFlag
CustomerCode
CustomerName
Terms
TermsDays
Currency
SubTotalAmount
SalesAmount
TotalAmount
TaxableAmount
NonTaxableAmount
TaxRate
TaxAmount
DiscountRate
DiscountAmount
ShippingAmount
ShippingTaxAmount
MiscAmount
MiscTaxAmount
ChargeAndAllowanceAmount
ChannelAmount
PaidAmount
CreditAmount
Balance
DepositAmount
SalesRep
SalesRep2
SalesRep3
SalesRep4
CommissionRate
CommissionRate2
CommissionRate3
CommissionRate4
TotalWeight
ActualWeight
CancelCode
SalesDivision
CustomerSource
Fulfillment Status
Financial Status
AmountRefunded
IsEdi
ShippingCarrier
ShippingClass
MainTrackingNumber
MainReturnTrackingNumber
ChannelNum
ChannelAccountNum
ChannelOrderID
SecondaryChannelOrderID
ShippingAccount
RefNum
CustomerPoNum
Carton
EndBuyerUserID
EndBuyerName
EndBuyerEmail
ShipToName
ShipToFirstName
ShipToLastName
ShipToCompany
ShipToAddressLine1
ShipToAddressLine2
ShipToAddressLine3
ShipToCity
ShipToState
ShipToPostalCode
ShipToCounty
ShipToCountry
ShipToEmail
ShipToDaytimePhone
BillToName
BillToCompany
BillToAddressLine1
BillToAddressLine2
BillToAddressLine3
BillToCity
BillToState
BillToPostalCode
BillToCounty
BillToCountry
BillToEmail
BillToDaytimePhone
Notes
ShippingCode
WarehouseCode
ShipmentID
DepartmentCode
DivisionCode
Seq
ItemDate
SKU
UPC
CustomerSKU
SKUTitle
LotNum
Description
UOM
PackType
PackQty
PackPrice
OrderPack
ShipPack
CancelledPack
OpenPack
OrderQty
ShipQty
CancelledQty
OpenQty
PriceRule
Price
DiscountPrice
ExtAmount
ItemTotalAmount
ShipAmount
CancelledAmount
OpenAmount
Stockable
Taxable
Costable
IsProfit
LotInDate
LotExpDate
DBChannelOrderLineRowID
ItemShippingAmount
ShippingCost
ItemTaxAmount
ItemShippingTaxAmount
ItemDiscountRate
ItemDiscountAmount
ItemNotes
ItemCancelCode
Lineitem fulfillment status
Lineitem taxable
ChannelItemID
EAN
MPN
ExternalBarcode
PodInfo

================================================
USER PARAMETERS (OBEY STRICTLY)

A) DATE RANGE
Use today's date to determine StartDate and EndDate.

Date logic:

1. If today is Tuesday, Wednesday, Thursday, or Friday:
	StartDate = today
	EndDate = today

2. If today is Monday:
	StartDate = last Saturday
	EndDate = today (Monday)

3. If today is Saturday or Sunday:
	StartDate = today
	EndDate = today

B) ORDER VOLUME
OrdersToGenerate = 20

OrdersToGenerate is the order count for ONE day.

If the resolved date range has multiple days,
total orders to generate must be:

TotalOrders = OrdersToGenerate * NumberOfDaysInDateRange

Example:
If date range covers Sat, Sun, Mon (3 days) and OrdersToGenerate = 20,
generate 60 total orders.

C) LINE QUANTITY LIMITS
MinOrderQtyPerLine = 1
MaxOrderQtyPerLine = 4

D) STYLE LIMITS (distinct SKUs per order)
MinStylesPerOrder = 1
MaxStylesPerOrder = 3

E) ORDER TOTAL LIMITS
MinOrderTotalAmount = 45
MaxOrderTotalAmount = 150

F) ECOMMERCE BEHAVIOR CONTROLS

%OrdersWithDiscount = 35
DiscountRateOptions = 0

%OrdersWithTax = 0
TaxRateOptions = 0

%OrdersWithShippingCharge = 90
ShippingAmountRange = 0.00 to 18.00

%OrdersPaid = 5-12

================================================
G) ORDER NUMBER CONTROL

SequenceNumberStart = 1

OrderNumber format must be:
yyyyMMdd-sequenceNumber

Example:
20260603-1
20260603-2

Generation rules:

1. Use OrderDate (yyyyMMdd) as the prefix of OrderNumber.
2. The first generated order of each date uses SequenceNumberStart.
3. Each subsequent order on the same date increments sequenceNumber by +1.
4. sequenceNumber must remain sequential with no gaps per date.
5. OrderNumber must be unique per order.

================================================
POST GENERATION PARAMETER UPDATE

After the dataset has been generated:

1. For each date in the generated dataset, identify the largest sequenceNumber used.
2. Calculate the next starting value:

NextSequenceNumberStart = LastSequenceNumber + 1

3. Return the updated parameter value for the next run.

Example:

If the last OrderNumber for 20260603 is 20260603-450

Return:

For 20260603, SequenceNumberStart = 451

================================================
SOURCE FILE RULES

Customers source:
data/Customer_source.csv

Customer-channel mapping source:
data\Customer-Channel-ChannelAccountMapping.csv

Use ONLY CustomerCode and CustomerName from data/Customer_source.csv.

CustomerCode and CustomerName must match exactly from the same row.

Populate ChannelNum and ChannelAccountNum using mapping:

CustomerCode → ChannelNum, ChannelAccountNum

For each order, ChannelNum and ChannelAccountNum must come from the same mapping row.

================================================
MANDATORY ADDRESS RULES

ShipTo fields must NOT be blank:

ShipToName
ShipToFirstName
ShipToLastName
ShipToCompany
ShipToAddressLine1
ShipToAddressLine2
ShipToAddressLine3
ShipToCity
ShipToState
ShipToPostalCode
ShipToCounty
ShipToCountry
ShipToEmail
ShipToDaytimePhone

Populate ShipTo fields from data/Customer_source.csv:

ShipName → ShipToName
Contact → ShipToFirstName
Contact2 → ShipToLastName
ShipCompany → ShipToCompany
ShipAddressLine1 → ShipToAddressLine1
ShipAddressLine2 → ShipToAddressLine2
ShipDescription → ShipToAddressLine3
ShipCity → ShipToCity
ShipState → ShipToState
ShipPostalCode → ShipToPostalCode
ShipCounty → ShipToCounty
ShipCountry → ShipToCountry
ShipEmail → ShipToEmail
ShipDaytimePhone → ShipToDaytimePhone

================================================
BILL TO RULE

BillTo fields are REQUIRED.

BillToName
BillToCompany
BillToAddressLine1
BillToAddressLine2
BillToAddressLine3
BillToCity
BillToState
BillToPostalCode
BillToCounty
BillToCountry
BillToEmail
BillToDaytimePhone

BillTo values may be copied from ShipTo values.

================================================
DAILY ORDER DISTRIBUTION RULE

Orders must be distributed across the date range.

Maximum orders per day = 20.

Ensure no single day exceeds 20 orders.

================================================
PRODUCT SOURCES

Use one single source file for SKU pool:

SKU_Only.csv

Rules:

SKU must come from SKU_Only.csv.

Do NOT repeat the same SKU within the same order.

Spread SKU usage across the dataset.

================================================
CSV STRUCTURE VALIDATION

Before generating rows:

ColumnCount = number of columns in the header.

Every generated row must contain exactly ColumnCount fields.

Never add columns.
Never skip columns.

================================================
ORDER GENERATION METHOD

STEP 1 — Generate Order Headers

Generate exactly OrdersToGenerate orders.

Each order must contain:

OrderNumber
ChannelOrderID
CustomerCode
CustomerName
ChannelNum
ChannelAccountNum
OrderDate

Ensure:

OrderNumber increments sequentially.
ChannelOrderID is unique per order.
No day exceeds 20 orders.

STEP 2 — Assign Line Items

For each order:

Determine NumStyles between MinStylesPerOrder and MaxStylesPerOrder.

For each style:

Select SKU from the SKU pool.

Ensure SKU is not repeated within the same order.

Generate:

OrderQty
Price
ExtAmount

================================================
PRICE RULE

Prices must be realistic for ecommerce orders.

Typical price range:
$12 to $80.

Prices should allow order totals to reach limits without excessive quantity adjustments.

================================================
ORDER TOTAL CALCULATION

ExtAmount = OrderQty * Price

SubTotalAmount = Sum(line ExtAmount) - DiscountAmount

TaxAmount = 0

TotalAmount = SubTotalAmount + ShippingAmount

================================================
HARD CONSTRAINT

MinOrderTotalAmount ≤ TotalAmount ≤ MaxOrderTotalAmount

If below minimum:
Increase quantity or add style.

If above maximum:
Reduce quantity or styles.

================================================
ORDER DEFAULT VALUES

OrderType = 1

OrderStatus = 0

Currency = USD

UOM = EA

Stockable = TRUE

Costable = TRUE

Taxable = TRUE

IsProfit = TRUE

ShipQty = 0

OpenQty = OrderQty

================================================
MANDATORY FIELD RULES (REQUIRED)

The following fields are mandatory and must be populated with these rules:

OrderNumber = yyyyMMdd-sequenceNumber using OrderDate as yyyyMMdd prefix.
Example for today: 20260312-1

OrderType = 1

OrderStatus = 0

ShipDate = OrderDate + 3 days

DueDate = ShipDate

BillDate = ShipDate + 7 days

ItemTotalAmount = ExtAmount

OpenAmount = ExtAmount - CancelledAmount - (ShipQty * Price)

Seq = line sequence number per order, starting at 1 and incrementing by 1 for each additional line in the same order

ShipAmount = 0

TaxRate = 0

If any mandatory field listed above does not have additional explanation elsewhere, use these rules as the default source of truth.

================================================
PAYMENT AND FULFILLMENT STATUS

Financial Status = ' '

Fulfillment Status = ' '

PaidAmount = 0

Balance = TotalAmount

================================================
CUSTOMER TYPE BASED ORDER RULES (APPENDED)

Customer source for Type must be:
data/Customer_source.csv

This file contains three Type values:

- Ecommerce
- Retail
- Wholesale

Type behavior rules:

1) Ecommerce
- Follow the current existing SalesOrder rules in this prompt.

2) Retail
- OrderQty and order amount for each order must be 2x of Ecommerce baseline behavior.
- Item Price must be MSRP * 0.8.
- Retail orders can only be placed on Monday.

3) Wholesale
- OrderQty and order amount for each order must be 4x of Ecommerce baseline behavior.
- Item Price must use WSP.
- Wholesale orders can only be placed on Wednesday.

Scheduling rule by Type:
- Ecommerce: follow current date logic in this prompt.
- Retail: only Monday.
- Wholesale: only Wednesday.

================================================
FINAL VALIDATION

Before output:

1. Exactly OrdersToGenerate unique orders exist.
2. No day exceeds 20 orders.
3. OrderNumber sequence has no gaps.
4. All ShipTo and BillTo fields are populated.
5. TotalAmount is within limits.
6. No SKU repeats within the same order.
7. Every row matches the header column count.
8. Mandatory fields (OrderNumber, OrderType, OrderStatus, ShipDate, DueDate, BillDate, ItemTotalAmount, OpenAmount, Seq, ShipAmount, TaxRate) are populated using the required rules.

================================================
FINAL OUTPUT

Generate exactly OrdersToGenerate orders.

Multiple rows per order if NumStyles > 1.

Output CSV only.