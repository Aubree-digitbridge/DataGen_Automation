Create a Python script for Visual Studio Code that processes product images from a local folder and generates a CSV file for ERP import.

INPUT / OUTPUT
- Input folder: ./images
- Supported file types: .jpg, .jpeg, .png, .webp
- Process images one by one until all images are completed
- Output file: products.csv
- One CSV row per image

GOAL
For each image, analyze the product visually and generate product attributes suitable for ERP, website, marketplace, and dropship content.

STRICT CONTENT RULES
1. Use only what can reasonably be identified from the image.
2. Do NOT invent UPC, ASIN, MSRP, Wholesale Price, Manufacturer, Country of Origin, or exact material percentages unless visible or provided.
3. If a value cannot be determined, leave it blank.
4. Assume fashion/apparel/accessories unless clearly indicated otherwise.
5. Generate clean, professional, SEO-friendly content.
6. Keep generated content aligned with visible product attributes (type, color, pattern, silhouette, style, material appearance).
7. Set Sub-Style Code equal to the image file name without extension.
8. Derive Style Code from Sub-Style Code using these exact rules:
   - If Sub-Style Code contains one '-', Style Code is the first segment.
   - If Sub-Style Code contains two or more '-', Style Code is the first and second segments joined with '-'.
   - Example: Sub-Style Code = CORA-01-YLW -> Style Code = CORA-01.

TECHNICAL REQUIREMENTS
1. Use Python.
2. Build a reusable script that loops through all images.
3. Generate products.csv with header + data rows.
4. Escape commas and quotes correctly for CSV output.
5. Log progress per image.
6. Add error handling so one failed image does not stop the batch.
7. Save failures to failed_images.txt.
8. Use modular functions such as:
   - get_image_files()
   - analyze_image()
   - generate_product_attributes()
   - write_to_csv()
9. Include maintainable comments in code.
10. Make it easy to add future attributes.

IMPLEMENTATION NOTE
- Structure analyze_image() and generate_product_attributes() so they can later be swapped with Copilot-assisted logic, OpenAI Vision logic, or manual business rules.
- For now, use clear placeholder logic that is production-structured and easy to extend.

CSV COLUMNS (use exactly this order and names)
Style Code,
Sub-Style Code,
AgeGroup,
ColorMap,
CountryofOrigin,
DetailImage,
DropshipListingTitle,
Gender,
Keywords,
MarketplaceItemName,
WebsiteLongDescription,
WebsiteProductLandingPage,
WebsiteProductTitle,
WebsiteShortDescription,
Custom Label 0,
Custom Label 1,
Custom Label 2,
Custom Label 3,
Custom Label 4,
Key Features 1,
Key Features 2,
Key Features 3,
Key Features 4,
Key Features 5,
Meta Description,
Meta Keywords,
Meta Title,
Dropship Description,
Dropship Short Description,
Product Long Description,
Product Short Description,
California Prop 65 Warning Text,
Color Selection,
Contained Battery Type,
Contains Chemical or Aerosol or Pesticide,
Contains Electronic Component,
Line Sheet Price,
Line Sheet Product Description,
Line Sheet Product Name,
Line Sheet Season,
Size Range,

CONTENT GUIDANCE FOR DESCRIPTIVE FIELDS
- Style Code: derive from Sub-Style Code based on dash rules.
- Sub-Style Code: image file name without extension.
- WebsiteProductTitle: SEO-friendly website title.
- MarketplaceItemName: marketplace-friendly title.
- DropshipListingTitle: concise retail listing title.
- WebsiteShortDescription: 1–2 sentence summary.
- WebsiteLongDescription: polished marketing description.
- Meta Title: concise SEO title.
- Meta Description: SEO description.
- Meta Keywords: keywords aligned to visible attributes.
- Keywords: keywords aligned to visible attributes.
- Dropship Description: reseller-friendly copy.
- Dropship Short Description: concise seller summary.
- Product Long Description: product detail long copy.
- Product Short Description: concise product summary.
- Key Features 1 to Key Features 5: visible features only.
- WebsiteProductLandingPage: SEO-friendly slug path.
- ColorMap: primary visible color map value.
- Color Selection: combined visible color values.
- AgeGroup: infer only when reasonable; otherwise leave blank.
- Gender: infer only when reasonable; otherwise leave blank.
- DetailImage: original image file name.

OUTPUT FORMAT REQUIREMENT
Return a complete Python script only.
Do not explain the script.
Do not return pseudocode.