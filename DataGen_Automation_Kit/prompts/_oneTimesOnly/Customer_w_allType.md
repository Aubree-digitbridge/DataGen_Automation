You are generating import-ready CSV data.

STRICT RULES (do not violate):

Output CSV ONLY. No explanations, no markdown, no code fences.

The first line MUST be the header row EXACTLY as provided.

Do NOT add/remove/rename columns.

Every row must have the same number of columns as the header.

Do not include blank lines.

If a field contains commas, wrap that field in double quotes.

ENTITY: Customer
ROWS TO GENERATE: 20

SPECIAL GENERATION RULES (MUST FOLLOW):

Randomly generate eCommerce CustomerCodes.

Include the following CustomerCodes :

eComm-AMZ-eCom
eComm-Veeqo-Amazon
eComm-eBay
eComm-Etsy-LS
eComm-Etsy-VS
eComm-JCPenney
eComm-Mirakl-Kohls
eComm-Macys
eComm-Magento
eComm-Shopify
eComm-Squarespace
eComm-Tiktok
eComm-Walmart-eComm

In addition to normal customers, you MUST generate:

Three Wholesale customers

Two Retail customers

WHOLESALE CUSTOMER RULES:

CustomerCode format:
wh-FirstWordOfCustomerName-FirstCharacterOfRemainingName

Example:
CustomerName = Golden State Apparel
CustomerCode = wh-Golden-SA

Generate exactly THREE Wholesale customers.

RETAIL CUSTOMER RULES:

CustomerCode format:
re-FirstWordOfCustomerName-FirstCharacterOfRemainingName

Example:
CustomerName = Pacific Fashion Boutique
CustomerCode = re-Pacific-FB

Generate exactly TWO Retail customers.

CustomerName must match the generated name used in the CustomerCode.

UNIQUENESS REQUIREMENTS:

Each row must have its own unique customer data (do not copy/paste the same values across customers).

Contact, Contact2, and Contact3 must each be in FirstName LastName format.

Contact, Contact2, and Contact3 must all be unique across the entire file (no duplicates in any of the three columns).

Contact2 MUST be unique in each row AND unique across the entire file (no duplicates).

Contact3 MUST be unique in each row AND unique across the entire file (no duplicates).

Email MUST be unique across the entire file.

Website MUST be unique across the entire file.

SalesRep and SalesRep2 MAY repeat across rows. All other fields should vary realistically.

BILLING CITY ↔ PHONE RULE (MUST FOLLOW):

Choose BillCity from the list below.

Phone numbers MUST match BillCity using BOTH:

1. The city's area code
2. The city's phone prefix (the first 3 digits after area code)

Use this format:
(AreaCode) Prefix-####

City mapping:

Los Angeles -> (213) 310-####
Irvine -> (949) 418-####
San Diego -> (619) 278-####
San Jose -> (408) 662-####
San Francisco -> (415) 794-####

Rules:

Phone1, Phone2, Phone3, Phone4 must all use the SAME BillCity area code and BillCity prefix for that row.

Phone1, Phone2, Phone3, and Phone4 must each be unique within the row and also unique across the entire file.

Phone1, Phone2, Phone3, and Phone4 must be consistent with the address location (BillCity / BillState area code mapping).

BillDaytimePhone must also use the SAME BillCity area code and BillCity prefix.

ShipDaytimePhone should also match ShipCity area code and ShipCity prefix (you may use the same city as billing to keep it consistent).

HEADER (must match exactly):

CustomerCode, CustomerName, Contact, Contact2, Contact3, Phone1, Phone2, Phone3, Phone4, Email, WebSite, FirstDate, Currency, CreditLimit, DiscountRate, Area, Region, Terms, TermsDays, SalesRep, SalesRep2, CommissionRate, CommissionRate2, BillName, BillCompany, BillAddressLine1, BillAddressLine2, BillCity, BillState, BillPostalCode, BillCounty, BillCountry, BillEmail, BillDaytimePhone, BillDescription, ShipName, ShipCompany, ShipAddressLine1, ShipAddressLine2, ShipCity, ShipState, ShipPostalCode, ShipCounty, ShipCountry, ShipEmail, ShipDaytimePhone, ShipDescription

FIELD GUIDANCE (KEEP DATA REALISTIC):

FirstDate: use dates between 2024-01-15 and 2024-02-03 (one per row; no need to be unique).
Currency: USD for all rows.
CreditLimit: vary values (example range: 15000 to 120000).
DiscountRate: vary small values (example: 0, 0.02, 0.05, 0.08, 0.10).
BillCountry/ShipCountry: USA
BillState/ShipState should match the city (use CA for all listed cities above).
Terms: choose among Net30 / Net45 / Net60 and vary per row.
TermsDays: must match Terms (Net30=30, Net45=45, Net60=60).
CommissionRate / CommissionRate2: vary reasonable decimals (example: 0.00 to 0.08).
Contact, Contact2, and Contact3 must be unique and must use FirstName LastName format.
Use different BillAddressLine1, BillPostalCode, ShipAddressLine1, ShipPostalCode per row.

FORMATTING:

Use YYYY-MM-DD for dates.
Use 2 decimal places for currency/amount fields when applicable.

Now output the CSV.