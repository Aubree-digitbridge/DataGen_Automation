You are generating import-ready CSV data.

Three CSV files will always be attached to this prompt:

1) Aubree_Lumo_Customer.csv
2) Aubree_Lumo_SKU.csv
3) Customer-Channel-ChannelAccountMapping.csv

You MUST read and use these files as the ONLY data sources.

================================================
STRICT RULES (DO NOT VIOLATE)

Output CSV ONLY.

No explanations.
No markdown.
No code blocks.

The first line MUST be the header row EXACTLY as provided below.

Do NOT add, remove, or rename columns.

Every row must contain the SAME number of columns as the header.

Do not include blank lines.

If a field contains commas, wrap the field in double quotes.

================================================
HEADER

OrderNumber	OrderType	OrderStatus	OrderDate	ShipDate	DueDate	BillDate	EtaArrivalDate	EarliestShipDate	LatestShipDate	SignatureFlag	CustomerCode	CustomerName	Terms	TermsDays	Currency	SubTotalAmount	SalesAmount	TotalAmount	TaxableAmount	NonTaxableAmount	TaxRate	TaxAmount	DiscountRate	DiscountAmount	ShippingAmount	ShippingTaxAmount	MiscAmount	MiscTaxAmount	ChargeAndAllowanceAmount	ChannelAmount	PaidAmount	CreditAmount	Balance	DepositAmount	SalesRep	SalesRep2	SalesRep3	SalesRep4	CommissionRate	CommissionRate2	CommissionRate3	CommissionRate4	TotalWeight	ActualWeight	CancelCode	SalesDivision	CustomerSource	Fulfillment Status	Financial Status	AmountRefunded	IsEdi	ShippingCarrier	ShippingClass	MainTrackingNumber	MainReturnTrackingNumber	ChannelNum	ChannelAccountNum	ChannelOrderID	SecondaryChannelOrderID	ShippingAccount	RefNum	CustomerPoNum	Carton	EndBuyerUserID	EndBuyerName	EndBuyerEmail	ShipToName	ShipToFirstName	ShipToLastName	ShipToCompany	ShipToAddressLine1	ShipToAddressLine2	ShipToAddressLine3	ShipToCity	ShipToState	ShipToPostalCode	ShipToCounty	ShipToCountry	ShipToEmail	ShipToDaytimePhone	BillToName	BillToCompany	BillToAddressLine1	BillToAddressLine2	BillToAddressLine3	BillToCity	BillToState	BillToPostalCode	BillToCounty	BillToCountry	BillToEmail	BillToDaytimePhone	Notes	ShippingCode	WarehouseCode	ShipmentID	DepartmentCode	DivisionCode	Seq	ItemDate	SKU	UPC	CustomerSKU	SKUTitle	LotNum	Description	UOM	PackType	PackQty	PackPrice	OrderPack	ShipPack	CancelledPack	OpenPack	OrderQty	ShipQty	CancelledQty	OpenQty	PriceRule	Price	DiscountPrice	ExtAmount	ItemTotalAmount	ShipAmount	CancelledAmount	OpenAmount	Stockable	Taxable	Costable	IsProfit	LotInDate	LotExpDate	DBChannelOrderLineRowID	ItemShippingAmount	ShippingCost	ItemTaxAmount	ItemShippingTaxAmount	ItemDiscountRate	ItemDiscountAmount	ItemNotes	ItemCancelCode	Lineitem fulfillment status	Lineitem taxable	ChannelItemID	EAN	MPN	ExternalBarcode	PodInfo

================================================
SOURCE DATA RULES

Customers must come ONLY from Aubree_Lumo_Customer.csv.

CustomerCode and CustomerName must come from the SAME row.

SKU must come ONLY from Aubree_Lumo_SKU.csv.

Use the Price column as the selling price.

Ignore SKUs where Price is blank or 0.

ChannelNum and ChannelAccountNum must come from
Customer-Channel-ChannelAccountMapping.csv.

Mapping rule:

CustomerCode → ChannelNum + ChannelAccountNum

If a CustomerCode does not exist in the mapping file,
skip that customer.

================================================
USER PARAMETERS

StartDate = 2026-03-05
EndDate = 2026-03-05

OrdersToGenerate = 20

MinOrderQtyPerLine = 1
MaxOrderQtyPerLine = 4

MinStylesPerOrder = 1
MaxStylesPerOrder = 3

MinOrderTotalAmount = 45
MaxOrderTotalAmount = 150

ShippingAmountRange = 0.00 to 18.00

================================================
ORDER NUMBER CONTROL

OrderNumberStart = 1

First order uses OrderNumberStart.

Each order increments by +1.

OrderNumber must remain numeric only.

================================================
POST GENERATION PARAMETER UPDATE

After generating the dataset:

Find the largest OrderNumber.

NextOrderNumberStart = LastOrderNumber + 1

Return the updated value.

Example

If last OrderNumber = 20

Return

OrderNumberStart = 21

================================================
ORDER GENERATION

Generate exactly OrdersToGenerate orders.

Each order must include:

OrderNumber
ChannelOrderID
CustomerCode
CustomerName
ChannelNum
ChannelAccountNum
OrderDate

ChannelOrderID must be unique.

Example:

AMZ-eCom-2026-000001

================================================
LINE ITEMS

For each order:

Select number of styles between MinStylesPerOrder and MaxStylesPerOrder.

Select unique SKUs from SKU file.

OrderQty must be between MinOrderQtyPerLine and MaxOrderQtyPerLine.

Price must come from the SKU file.

ExtAmount = OrderQty × Price

================================================
TOTAL CALCULATION

SubTotalAmount = sum of ExtAmount

TaxAmount = 0

TotalAmount = SubTotalAmount + ShippingAmount

================================================
TOTAL CONSTRAINT

MinOrderTotalAmount ≤ TotalAmount ≤ MaxOrderTotalAmount

If below minimum:
increase quantity or add SKU.

If above maximum:
reduce quantity or styles.

================================================
DEFAULT VALUES

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

Financial Status = ' '
Fulfillment Status = ' '

PaidAmount = 0
Balance = TotalAmount

================================================
ADDRESS RULES

Generate realistic US addresses.

Phone format:

(xxx) xxx-xxxx

BillTo fields may copy ShipTo fields.

================================================
FINAL VALIDATION

Orders generated = OrdersToGenerate

OrderNumber sequence has no gaps.

ChannelNum and ChannelAccountNum match mapping file.

No SKU repeats within the same order.

TotalAmount within limits.

All rows match header column count.

================================================
FINAL OUTPUT

Generate exactly 20 orders following all logic above.

Package this data into a .csv file.

Provide the download link for import_ready_orders.csv.

Immediately following the file generation, provide the POST GENERATION PARAMETER UPDATE (e.g., NextOrderNumberStart = 21) as the only text visible in the chat.