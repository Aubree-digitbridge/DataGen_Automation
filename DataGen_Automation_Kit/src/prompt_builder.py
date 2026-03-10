from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PromptRequest:
    entity_name: str
    headers: List[str]
    row_count: int

    # Optional dataset context
    dataset_type: Optional[str] = None  # "historical" | "current" | None
    date_range: Optional[Dict[str, str]] = None  # {"start_date": "...", "end_date": "..."}

    # Schema rules
    required_fields: Optional[List[str]] = None
    primary_key: Optional[List[str]] = None
    enums: Optional[Dict[str, List[str]]] = None
    foreign_keys: Optional[Dict[str, Dict[str, str]]] = None  # {field: {"entity": "...", "field": "..."}}

    # Extra business rules (your existing config key: business_rules)
    extra_rules: Optional[List[str]] = None

    # Seed lists for foreign keys / controlled fields (e.g., valid CustomerCode list)
    seed_lists: Optional[Dict[str, List[str]]] = None  # {field: [values...]}

    # NEW: fixed list generation rules (ex: CustomerCode fixed list)
    fixed_values: Optional[Dict[str, List[str]]] = None  # {"CustomerCode": [..]}

    # NEW: derived field rules (ex: CustomerName from CustomerCode)
    derived_rules: Optional[List[str]] = None

    # NEW: uniqueness control (ex: only SalesRep/SalesRep2 may repeat)
    repeatable_fields: Optional[List[str]] = None
    uniqueness_rule: Optional[str] = None


def _fmt_list(values: List[str], max_items: int = 50) -> str:
    """
    Formats a list of values for prompts, limiting length to avoid overly long prompts.
    """
    if not values:
        return ""
    if len(values) <= max_items:
        return ", ".join(values)
    head = ", ".join(values[:max_items])
    return f"{head}, ... (+{len(values) - max_items} more)"


def build_copilot_prompt(req: PromptRequest) -> str:
    headers_csv = ", ".join(req.headers)

    required = req.required_fields or []
    pk = req.primary_key or []
    enums = req.enums or {}
    fks = req.foreign_keys or {}
    extra_rules = req.extra_rules or []
    seed_lists = req.seed_lists or {}

    fixed_values = req.fixed_values or {}
    derived_rules = req.derived_rules or []
    repeatable = req.repeatable_fields or []
    uniqueness_rule = req.uniqueness_rule

    lines: List[str] = []

    # Core strict rules
    lines.append("You are generating import-ready CSV data.")
    lines.append("STRICT RULES (do not violate):")
    lines.append("1) Output CSV ONLY. No explanations, no markdown, no code fences.")
    lines.append("2) The first line MUST be the header row EXACTLY as provided.")
    lines.append("3) Do NOT add/remove/rename columns.")
    lines.append("4) Every row must have the same number of columns as the header.")
    lines.append("5) Do not include blank lines.")
    lines.append("6) Do not add comments before/after the CSV.")
    lines.append("")

    # Entity info
    lines.append(f"ENTITY: {req.entity_name}")
    if req.dataset_type:
        lines.append(f"DATASET TYPE: {req.dataset_type.upper()}")
    lines.append(f"ROWS TO GENERATE: {req.row_count}")
    lines.append("")

    # Header
    lines.append("HEADER (must match exactly):")
    lines.append(headers_csv)
    lines.append("")

    # Date range (if present)
    if req.date_range:
        lines.append(f"DATE RANGE: {req.date_range['start_date']} to {req.date_range['end_date']}")
        lines.append("All date fields must fall in this range.")
        lines.append("")

    # PK / Required
    if pk:
        lines.append(f"PRIMARY KEY (must be unique): {', '.join(pk)}")
    if required:
        lines.append(f"REQUIRED FIELDS (not blank): {', '.join(required)}")

    # Foreign keys
    if fks:
        lines.append("")
        lines.append("FOREIGN KEY RULES:")
        for field, ref in fks.items():
            lines.append(f"- {field} must reference an existing {ref['entity']}.{ref['field']}")

    # Seed lists (help Copilot pick valid FK values)
    if seed_lists:
        lines.append("")
        lines.append("SEED LISTS (use these values where applicable):")
        for field, values in seed_lists.items():
            if values:
                lines.append(f"- {field}: {_fmt_list(values, max_items=60)}")

    # Enums
    if enums:
        lines.append("")
        lines.append("ENUM RULES (use ONLY allowed values):")
        for field, allowed in enums.items():
            lines.append(f"- {field}: {allowed}")

    # SPECIAL generation rules (fixed values + derived rules)
    if fixed_values or derived_rules:
        lines.append("")
        lines.append("SPECIAL GENERATION RULES:")

        # If there is a fixed list for a known field (ex: CustomerCode)
        for field_name, values in fixed_values.items():
            if values:
                lines.append(f"- The number of rows MUST equal the number of '{field_name}' entries listed below ({len(values)}).")
                lines.append(f"- Generate exactly ONE row per '{field_name}'.")
                lines.append(f"- Use EXACTLY these '{field_name}' values and no others.")
                lines.append("")
                lines.append(f"{field_name} list:")
                for v in values:
                    lines.append(v)

        if derived_rules:
            lines.append("")
            lines.append("Derived field rules:")
            for r in derived_rules:
                lines.append(f"- {r}")

    # Uniqueness requirement (your new Customer requirement)
    if uniqueness_rule:
        lines.append("")
        lines.append("UNIQUENESS REQUIREMENT:")
        lines.append(f"- {uniqueness_rule}")
        if repeatable:
            lines.append(f"- Fields allowed to repeat: {', '.join(repeatable)}")

    # Extra business rules (generic)
    if extra_rules:
        lines.append("")
        lines.append("BUSINESS RULES:")
        for r in extra_rules:
            lines.append(f"- {r}")

    # Formatting guidance
    lines.append("")
    lines.append("FORMATTING:")
    lines.append("- Use YYYY-MM-DD for dates.")
    lines.append("- Use 2 decimal places for currency/amount fields when applicable.")
    lines.append("- Quote fields if they contain commas.")
    lines.append("")
    lines.append("Now output the CSV.")

    return "\n".join(lines)