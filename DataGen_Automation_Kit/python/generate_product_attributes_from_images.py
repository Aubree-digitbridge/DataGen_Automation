from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path
from typing import Iterable

# Input / output settings
IMAGES_DIR = Path("./images")
OUTPUT_DIR = Path("./output")
OUTPUT_CSV = OUTPUT_DIR / "products.csv"
FAILED_LOG = OUTPUT_DIR / "failed_images.txt"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
TAXONOMY_CONFIG_FILE = Path("./python/taxonomy_overrides.json")

# CSV schema (exact names/order requested)
CSV_COLUMNS = [
    "Style Code",
    "Sub-Style Code",
    "AgeGroup",
    "ColorMap",
    "CountryofOrigin",
    "DetailImage",
    "DropshipListingTitle",
    "Gender",
    "Keywords",
    "MarketplaceItemName",
    "WebsiteLongDescription",
    "WebsiteProductLandingPage",
    "WebsiteProductTitle",
    "WebsiteShortDescription",
    "Custom Label 0",
    "Custom Label 1",
    "Custom Label 2",
    "Custom Label 3",
    "Custom Label 4",
    "Key Features 1",
    "Key Features 2",
    "Key Features 3",
    "Key Features 4",
    "Key Features 5",
    "Meta Description",
    "Meta Keywords",
    "Meta Title",
    "Dropship Description",
    "Dropship Short Description",
    "Product Long Description",
    "Product Short Description",
    "California Prop 65 Warning Text",
    "Color Selection",
    "Contained Battery Type",
    "Contains Chemical or Aerosol or Pesticide",
    "Contains Electronic Component",
    "Line Sheet Price",
    "Line Sheet Product Description",
    "Line Sheet Product Name",
    "Line Sheet Season",
    "Size Range",
]


def get_image_files(images_dir: Path) -> list[Path]:
    if not images_dir.exists() or not images_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {images_dir.resolve()}")

    files = [
        p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files, key=lambda x: x.name.lower())


def _normalize_tokens(file_stem: str) -> list[str]:
    tokens = re.split(r"[^A-Za-z0-9]+", file_stem)
    return [token for token in tokens if token]


def _derive_style_code(substyle_code: str) -> str:
    dash_count = substyle_code.count("-")
    parts = substyle_code.split("-")

    if dash_count == 1:
        return parts[0] if parts else substyle_code
    if dash_count >= 2:
        return "-".join(parts[:2]) if len(parts) >= 2 else substyle_code
    return substyle_code


def _validate_style_fields(style_code: str, substyle_code: str) -> None:
    if not substyle_code or not substyle_code.strip():
        raise ValueError("Style/Substyle validation failed: Sub-Style Code is blank")
    if not style_code or not style_code.strip():
        raise ValueError(
            f"Style/Substyle validation failed: Style Code is blank for Sub-Style Code '{substyle_code}'"
        )


def _taxonomy_from_product_type(product_type: str) -> dict[str, str]:
    taxonomy = {
        "Category": "Apparel",
        "Class": "Fashion",
        "Subcategory": "General",
        "Group": "Apparel & Accessories",
        "Subgroup": "Fashion Item",
        "Division": "Women",
        "Department": "Women",
        "Gender": "Women",
        "Age Group": "Adult",
    }

    if product_type == "Dress":
        taxonomy.update(
            {
                "Category": "Apparel",
                "Class": "Dresses",
                "Subcategory": "Womens Dresses",
                "Group": "Womens Apparel",
                "Subgroup": "Dresses",
            }
        )
    elif product_type == "Top":
        taxonomy.update(
            {
                "Category": "Apparel",
                "Class": "Tops",
                "Subcategory": "Womens Tops",
                "Group": "Womens Apparel",
                "Subgroup": "Tops",
            }
        )
    elif product_type == "Bottom":
        taxonomy.update(
            {
                "Category": "Apparel",
                "Class": "Bottoms",
                "Subcategory": "Womens Bottoms",
                "Group": "Womens Apparel",
                "Subgroup": "Bottoms",
            }
        )
    elif product_type == "Footwear":
        taxonomy.update(
            {
                "Category": "Footwear",
                "Class": "Shoes",
                "Subcategory": "Womens Shoes",
                "Group": "Womens Footwear",
                "Subgroup": "Fashion Shoes",
                "Division": "Footwear",
                "Department": "Footwear",
            }
        )

    return taxonomy


def load_taxonomy_overrides(config_path: Path) -> dict[str, dict[str, str]]:
    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return {}

    cleaned: dict[str, dict[str, str]] = {}
    for key, value in data.items():
        if isinstance(key, str) and isinstance(value, dict):
            cleaned[key] = {str(k): str(v) for k, v in value.items()}
    return cleaned


def analyze_image(image_path: Path) -> dict[str, str]:
    """
    Placeholder visual-analysis logic.
    Replace this with CV / AI vision logic later.
    """
    stem = image_path.stem
    tokens = _normalize_tokens(stem)
    lowered = [t.lower() for t in tokens]

    color_candidates = {
        "black": "Black",
        "white": "White",
        "pink": "Pink",
        "blue": "Blue",
        "green": "Green",
        "red": "Red",
        "yellow": "Yellow",
        "nude": "Nude",
        "camel": "Camel",
        "taupe": "Taupe",
        "grey": "Grey",
        "gray": "Gray",
        "brown": "Brown",
        "beige": "Beige",
        "lilac": "Lilac",
        "ginger": "Ginger",
        "cherry": "Cherry",
        "blush": "Blush",
    }

    detected_colors = []
    for key, label in color_candidates.items():
        if key in lowered and label not in detected_colors:
            detected_colors.append(label)

    if not detected_colors:
        detected_colors = [""]

    color_primary = detected_colors[0]
    color_secondary = detected_colors[1] if len(detected_colors) > 1 else ""

    footwear_style_codes = {"adeline", "astrid", "austin", "aviana", "camila", "cora"}

    if any(x in lowered for x in ["dress", "maxi", "kimono"]):
        product_type = "Dress"
        category = "Apparel"
        subcategory = "Dresses"
    elif any(x in lowered for x in ["jean", "denim", "pant"]):
        product_type = "Bottom"
        category = "Apparel"
        subcategory = "Pants"
    elif any(x in lowered for x in ["blouse", "top", "shirt"]):
        product_type = "Top"
        category = "Apparel"
        subcategory = "Tops"
    elif any(x in lowered for x in ["sandal", "boot", "shoe"]) or any(x in lowered for x in footwear_style_codes):
        product_type = "Footwear"
        category = "Footwear"
        subcategory = "Shoes"
    else:
        product_type = "Fashion Item"
        category = "Apparel"
        subcategory = "General"

    title_tokens = [t for t in tokens if not t.isdigit()][:7]
    fallback_title = " ".join(title_tokens).strip() or "Fashion Product"

    return {
        "file_name": image_path.name,
        "file_stem": stem,
        "title_seed": fallback_title,
        "product_type": product_type,
        "category": category,
        "subcategory": subcategory,
        "color_primary": color_primary,
        "color_secondary": color_secondary,
    }


def generate_product_attributes(
    image_analysis: dict[str, str], taxonomy_overrides: dict[str, dict[str, str]]
) -> dict[str, str]:
    """
    Create one CSV row dict from analysis.
    Keeps unknown fields blank per requirements.
    """
    substyle_code = image_analysis["file_stem"]
    style_code = _derive_style_code(substyle_code)
    _validate_style_fields(style_code, substyle_code)
    title_seed = image_analysis["title_seed"]
    product_type = image_analysis["product_type"]
    category = image_analysis["category"]
    subcategory = image_analysis["subcategory"]
    color_primary = image_analysis["color_primary"]
    color_secondary = image_analysis["color_secondary"]
    taxonomy = _taxonomy_from_product_type(product_type)
    taxonomy.update(taxonomy_overrides.get("default", {}))
    taxonomy.update(taxonomy_overrides.get(product_type, {}))

    color_phrase = f"{color_primary} " if color_primary else ""
    erp_product_name = f"{color_phrase}{product_type}".strip() if product_type else title_seed
    website_title = f"{erp_product_name} | Fashion Collection".strip()

    short_desc = (
        f"{erp_product_name} designed for everyday wear with a modern fashion-forward look."
    )
    long_desc = (
        f"The {erp_product_name.lower()} offers a clean silhouette and versatile styling for multiple occasions. "
        f"This product is generated from image-based attributes and can be refined with additional catalog data."
    )

    key_features = [
        f"Visible color: {color_primary}" if color_primary else "Color visible in image",
        f"Product type: {product_type}",
        "Fashion-forward silhouette",
        "Suitable for styling across seasons",
        "Image-based placeholder attributes (review before publishing)",
    ]

    keyword_parts = [part for part in [product_type, color_primary, subcategory, "fashion"] if part]
    keywords = ", ".join(dict.fromkeys([k.lower() for k in keyword_parts]))

    row = {column: "" for column in CSV_COLUMNS}

    row["Style Code"] = style_code
    row["Sub-Style Code"] = substyle_code
    row["AgeGroup"] = taxonomy["Age Group"]
    row["ColorMap"] = color_primary
    row["CountryofOrigin"] = ""
    row["DetailImage"] = image_analysis["file_name"]
    row["DropshipListingTitle"] = erp_product_name
    row["Gender"] = taxonomy["Gender"]
    row["Keywords"] = keywords
    row["MarketplaceItemName"] = website_title
    row["WebsiteLongDescription"] = long_desc

    slug = re.sub(r"[^a-z0-9]+", "-", erp_product_name.lower()).strip("-")
    row["WebsiteProductLandingPage"] = f"/products/{slug}" if slug else ""
    row["WebsiteProductTitle"] = website_title
    row["WebsiteShortDescription"] = short_desc

    row["Custom Label 0"] = ""
    row["Custom Label 1"] = ""
    row["Custom Label 2"] = ""
    row["Custom Label 3"] = ""
    row["Custom Label 4"] = ""

    row["Key Features 1"] = key_features[0]
    row["Key Features 2"] = key_features[1]
    row["Key Features 3"] = key_features[2]
    row["Key Features 4"] = key_features[3]
    row["Key Features 5"] = key_features[4]

    row["Meta Description"] = long_desc[:155]
    row["Meta Keywords"] = keywords
    row["Meta Title"] = website_title[:70]
    row["Dropship Description"] = long_desc
    row["Dropship Short Description"] = short_desc
    row["Product Long Description"] = long_desc
    row["Product Short Description"] = short_desc
    row["California Prop 65 Warning Text"] = ""
    row["Color Selection"] = ", ".join([c for c in [color_primary, color_secondary] if c])
    row["Contained Battery Type"] = ""
    row["Contains Chemical or Aerosol or Pesticide"] = ""
    row["Contains Electronic Component"] = ""
    row["Line Sheet Price"] = ""
    row["Line Sheet Product Name"] = erp_product_name
    row["Line Sheet Product Description"] = short_desc
    row["Line Sheet Season"] = ""
    row["Size Range"] = ""

    return row


def write_to_csv(output_csv: Path, rows: Iterable[dict[str, str]]) -> None:
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        image_files = get_image_files(IMAGES_DIR)
    except Exception as exc:
        logging.error(f"Failed to scan images folder: {exc}")
        return

    if not image_files:
        logging.info("No supported image files found.")
        return

    logging.info(f"Found {len(image_files)} image files in {IMAGES_DIR}")
    taxonomy_overrides = load_taxonomy_overrides(TAXONOMY_CONFIG_FILE)
    if taxonomy_overrides:
        logging.info(f"Loaded taxonomy overrides from {TAXONOMY_CONFIG_FILE}")

    output_rows: list[dict[str, str]] = []
    failures: list[tuple[str, str]] = []
    style_substyle_validated_count = 0

    for idx, image_path in enumerate(image_files, start=1):
        logging.info(f"[{idx}/{len(image_files)}] Processing {image_path.name}")
        try:
            analysis = analyze_image(image_path)
            row = generate_product_attributes(analysis, taxonomy_overrides)
            output_rows.append(row)
            style_substyle_validated_count += 1
        except Exception as exc:
            if isinstance(exc, ValueError) and "Style/Substyle validation failed" in str(exc):
                raise
            failures.append((image_path.name, str(exc)))
            logging.info(f"[{idx}/{len(image_files)}] FAILED {image_path.name}: {exc}")

    write_to_csv(OUTPUT_CSV, output_rows)
    logging.info(f"CSV written: {OUTPUT_CSV.resolve()} ({len(output_rows)} rows)")

    if failures:
        with FAILED_LOG.open("w", encoding="utf-8") as f:
            for file_name, error in failures:
                f.write(f"{file_name}\nERROR: {error}\n\n")
        logging.info(f"Completed with {len(failures)} failures. Log: {FAILED_LOG.resolve()}")
    else:
        if FAILED_LOG.exists():
            FAILED_LOG.unlink(missing_ok=True)
        logging.info("Completed with no failures.")

    logging.info(
        f"Style/Substyle validation passed for {style_substyle_validated_count} row(s)."
    )


if __name__ == "__main__":
    main()
