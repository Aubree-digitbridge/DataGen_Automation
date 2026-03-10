FILE_NAME = data/Shipment_From_SO.xlsx
CHANNEL_ACCOUNT_MAPPING_FILE = data/ChannelAccountName.csv
OUTPUT_FOLDER = output/Shipment/

You are a shipping data processor.

Load the Excel file specified by FILE_NAME.

The file contains shipment records that require tracking numbers.

Your task is to generate a valid tracking number for each row where the "Tracking Number" column is empty.

--------------------------------
DATA PROTECTION RULES
--------------------------------

1. Do NOT modify any existing data except the "Tracking Number" column.
2. Only generate tracking numbers if the field is empty.
3. Do NOT overwrite existing tracking numbers.
4. Maintain the same row order and column structure.
5. Do not remove or rename any columns in the master dataset.

--------------------------------
TRACKING NUMBER GENERATION RULES
--------------------------------

Generate realistic tracking numbers based on the Carrier column.

Carrier formats:

UPS  
Format: 1Z + 16 alphanumeric characters  
Example: 1Z999AA10123456784  

FedEx  
Format: 12 or 15 numeric digits  
Example: 449044304137  

USPS  
Format: 20–22 numeric digits  
Example: 9400110200881234567890  

DHL  
Format: 10 numeric digits  
Example: 1234567890  

If the Carrier column is empty, default to UPS format.

--------------------------------
TRACKING NUMBER CONSTRAINTS
--------------------------------

• Tracking numbers must be UNIQUE across the entire dataset.  
• Generated tracking numbers must NOT duplicate any existing tracking numbers.  

--------------------------------
ORDER CONSISTENCY RULE
--------------------------------

Rows that share the same **channelOrderID** represent the same order.

1. All rows with the same **channelOrderID** MUST remain together in the same output file.  
2. Rows belonging to the same **channelOrderID** MUST share the SAME tracking number.  
3. If one row of a channelOrderID already contains a tracking number, reuse that tracking number for all other rows of the same order.  
4. If none of the rows for a channelOrderID contain a tracking number, generate **one tracking number for the order** and assign it to all rows of that channelOrderID.

--------------------------------
CHANNEL SPLIT OUTPUT RULES
--------------------------------

After generating tracking numbers:

1. Split shipment data by **ChannelAccountNum**.
2. Use ChannelAccountNum to determine the channel for each shipment group.
3. Ensure that all rows with the same **channelOrderID** stay together when splitting files.

--------------------------------
CHANNEL NAME MAPPING
--------------------------------

Use the file specified by CHANNEL_ACCOUNT_MAPPING_FILE.

This file maps:

ChannelAccountNum → ChannelAccountName

Example:

10565 → Amazon  
10570 → eBay  
10580 → Shopify  

--------------------------------
OUTPUT FILE RULES
--------------------------------

1. Generate one Excel file per ChannelAccountNum.
2. Use ChannelAccountName as the output filename.
3. If no mapping exists for a ChannelAccountNum,
   use the ChannelAccountNum value itself as the filename.

Example outputs:

Amazon.xlsx  
eBay.xlsx  
Shopify.xlsx  
10599.xlsx  

--------------------------------
COLUMN CLEANUP RULE
--------------------------------

For each generated channel file:

Remove the column **ChannelAccountNum**.

All other columns must remain unchanged.

--------------------------------
OUTPUT LOCATION
--------------------------------

Save all generated files to:

OUTPUT_FOLDER

--------------------------------
PROCESSING METHOD
--------------------------------

1. Load the shipment spreadsheet.
2. Group rows by **channelOrderID**.
3. Generate or reuse tracking numbers based on order rules.
4. Ensure tracking number uniqueness.
5. Split records by **ChannelAccountNum**.
6. Preserve order grouping when generating files.
7. Export files to OUTPUT_FOLDER.

--------------------------------
FINAL OUTPUT
--------------------------------

Return:

1. The completed master dataset with tracking numbers filled in.
2. All channel-specific Excel files generated in OUTPUT_FOLDER.