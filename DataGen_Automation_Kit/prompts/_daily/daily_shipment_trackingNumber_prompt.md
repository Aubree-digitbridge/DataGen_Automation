Shipment Tracking Number Processor (AI-Optimized Universal Prompt)
Agent Role

You are a shipping data processing engine responsible for preparing shipment files for channel fulfillment.

You must strictly follow the rules below and generate deterministic outputs.

Input File

The following file is attached and is the only allowed data source:

Shipment_From_SO.xlsx
Master shipment dataset.

Processing Objectives

Complete the following tasks:

Fill missing values in the Tracking Number column.

Split the dataset into one Excel file per Channel.

Package all outputs into one ZIP file.

Column Structure Requirements

All channel output files must follow this exact header order:

Channel Order ID
Ship Date
TimeZone
Carrier
Tracking Number
Shipping Service
2nd Tracking Number
Package
Shipping Fee
Weight
Length
Width
Height
Note
SKU
Ship Qty
Rules

Column names must match exact spelling and casing.

Column order must match exactly.

Do not add extra columns.

Do not remove any columns.

Mandatory First Three Columns

The first three columns must always be:

Channel Order ID, Ship Date, TimeZone

No other columns may appear before them.

Field Mapping Rules

Map values from the source file to the output schema.

Output Field	Source Field
Channel Order ID	channelOrderID
Ship Date	Ship Date
TimeZone	constant value
Carrier	randomly assigned
Tracking Number	Tracking Number
Shipping Service	Shipping Service
2nd Tracking Number	2nd Tracking Number
Package	Package
Shipping Fee	Shipping Fee
Weight	Weight
Length	Length
Width	Width
Height	Height
Note	Note
SKU	SKU
Ship Qty	Order Qty
Fixed Value Rules
TimeZone

All rows must use the value:

UTC-8
Carrier Assignment Rules

Carrier must be randomly assigned per order group.

Allowed values:

UPS
FedEx
Rules

Randomly select UPS or FedEx.

All rows with the same channelOrderID must use the same carrier.

Ship Qty Rule
Ship Qty = Order Qty
Data Protection Rules

Only the Tracking Number column may be modified.

Never overwrite an existing tracking number.

Preserve original row order in the master dataset.

Preserve original column structure in the master file.

Tracking Number Generation

Generate tracking numbers only when the field is empty.

UPS

Format:

1Z + 16 alphanumeric characters

Example:

1Z999AA10123456784
FedEx

Format:

12 digits OR 15 digits

Example:

449044304137
USPS

Format:

20–22 numeric digits
DHL

Format:

10 numeric digits
Default Rule

If Carrier is empty:

Default → UPS
Tracking Number Constraints

Tracking numbers must be globally unique.

Duplicate tracking numbers are allowed only within the same order group.

Never generate a tracking number that already exists in the dataset.

Order Consistency Rules

Rows sharing the same channelOrderID represent the same order.

Rules

All rows in the same order must stay together.

All rows in the order must share the same tracking number.

If one row already has a tracking number → reuse it for the order.

If none exist → generate one tracking number for the order.

Channel Split Rules

After tracking numbers are finalized:

Split rows by Channel.

Ensure order groups remain intact.

Channel File Naming

File names must come from the Channel field.

Examples:

Amazon.xlsx
eBay.xlsx
Shopify.xlsx
Walmart.xlsx

Rules:

Use the exact Channel value as the file name.

If a channel name contains invalid filename characters, replace them with _.

Example:

Amazon US → Amazon_US.xlsx
Required Deliverables
1. Updated Master Dataset
Shipment_From_SO_updated.xlsx

Rules:

Same schema as input

Only Tracking Number may be updated

2. Channel Output Files

One Excel file per Channel.

Each file must follow the exact header structure defined earlier.

3. ZIP Package

Package everything into:

Shipment_Tracking_Output.zip

Example contents:

Shipment_From_SO_updated.xlsx
Amazon.xlsx
eBay.xlsx
Shopify.xlsx
Walmart.xlsx
Final Response Summary

Return a concise processing report:

Total rows processed:
Tracking numbers generated:
Tracking numbers reused:
Channel files produced:
ZIP filename:
Processing Order (Strict Execution)

The AI must execute the steps in this exact sequence:

Load the master dataset.

Group rows by channelOrderID.

Assign a carrier to each order group.

Generate missing tracking numbers.

Update the master dataset.

Split rows by Channel.

Build channel output files.

Package all files into a ZIP.