import json
from pathlib import Path

from template_reader import read_headers
from prompt_builder import PromptRequest, build_copilot_prompt
from validate import (
    read_csv,
    validate_required,
    validate_unique,
    validate_foreign_keys,
    validate_date_range,
    build_index,
)

ROOT = Path(__file__).resolve().parents[1]


def load_rules():
    p = ROOT / "rules" / "rules.json"
    return json.loads(p.read_text(encoding="utf-8"))


def write_prompt(name: str, text: str):
    out_dir = ROOT / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / name).write_text(text, encoding="utf-8")


def try_read_seed_values(path: Path, field: str, limit: int = 2000):
    """
    Reads distinct values for `field` from a CSV file to be used as a seed list in prompts.
    """
    if not path.exists():
        return []
    _, rows = read_csv(path)
    vals = []
    seen = set()
    for r in rows:
        v = (r.get(field) or "").strip()
        if v and v not in seen:
            vals.append(v)
            seen.add(v)
        if len(vals) >= limit:
            break
    return vals


def build_master_indexes(rules):
    """
    Builds indexes for primary keys from available data sources.
    Priority: generated outputs (output_path) -> seed_path
    """
    indexes = {}
    for entity, cfg in rules["entities"].items():
        indexes.setdefault(entity, {})
        pk = cfg.get("primary_key", [])
        if not pk:
            continue

        candidates = []
        for k in ["output_path", "seed_path"]:
            if cfg.get(k):
                candidates.append(ROOT / cfg[k])

        for p in candidates:
            if not p.exists():
                continue
            headers, rows = read_csv(p)
            for f in pk:
                if f in headers:
                    indexes[entity][f] = build_index(rows, f)
            break

    return indexes


def _build_seed_lists(cfg: dict, master_indexes: dict) -> dict | None:
    """
    For each FK field, provide a seed list of allowed values from the referenced entity index.
    """
    seeds = {}
    for fk_field, ref in cfg.get("foreign_keys", {}).items():
        ent = ref["entity"]
        fld = ref["field"]
        seeds[fk_field] = sorted(list(master_indexes.get(ent, {}).get(fld, [])))[:500]
    return seeds or None


def cmd_generate_prompts():
    rules = load_rules()
    master_indexes = build_master_indexes(rules)

    for entity, cfg in rules["entities"].items():
        # A "split" entity has historical/current templates
        is_split = bool(cfg.get("template_path_historical") or cfg.get("template_path_current"))

        common_kwargs = dict(
            required_fields=cfg.get("required", []),
            primary_key=cfg.get("primary_key", []),
            enums=cfg.get("enums", {}),
            foreign_keys=cfg.get("foreign_keys", {}),
            extra_rules=cfg.get("business_rules", []),
            seed_lists=_build_seed_lists(cfg, master_indexes),
            # NEW: fixed list + derived rules + uniqueness rules
            fixed_values=cfg.get("fixed_values", None),
            derived_rules=cfg.get("derived_rules", None),
            repeatable_fields=cfg.get("repeatable_fields", None),
            uniqueness_rule=cfg.get("uniqueness_rule", None),
        )

        if not is_split:
            tmpl = read_headers(
                str(ROOT / cfg["template_path"]),
                sheet_name=cfg.get("template_sheet"),
            )

            req = PromptRequest(
                entity_name=entity,
                headers=tmpl.headers,
                row_count=cfg.get("default_rows", 50),
                **common_kwargs,
            )
            write_prompt(f"{entity}_prompt.txt", build_copilot_prompt(req))

        else:
            for dataset_type in ["historical", "current"]:
                tkey = f"template_path_{dataset_type}"
                if not cfg.get(tkey):
                    continue

                tmpl = read_headers(
                    str(ROOT / cfg[tkey]),
                    sheet_name=cfg.get(f"template_sheet_{dataset_type}") or cfg.get("template_sheet"),
                )

                req = PromptRequest(
                    entity_name=entity,
                    headers=tmpl.headers,
                    row_count=cfg.get(
                        f"default_rows_{dataset_type}",
                        200 if dataset_type == "historical" else 50,
                    ),
                    dataset_type=dataset_type,
                    date_range=rules["datasets"][dataset_type],
                    **common_kwargs,
                )
                write_prompt(f"{entity}_{dataset_type}_prompt.txt", build_copilot_prompt(req))

    print("✅ Prompts generated under /prompts")


def cmd_validate():
    rules = load_rules()
    master_indexes = build_master_indexes(rules)

    all_errors = []

    for entity, cfg in rules["entities"].items():
        paths = []
        for k in ["output_path", "output_path_historical", "output_path_current"]:
            if cfg.get(k):
                paths.append(cfg[k])

        for rel in paths:
            p = ROOT / rel
            if not p.exists():
                continue

            headers, rows = read_csv(p)
            required = cfg.get("required", [])
            pk = cfg.get("primary_key", [])
            fks = cfg.get("foreign_keys", {})

            errs = []
            errs += validate_required(rows, required)
            errs += validate_unique(rows, pk)
            if fks:
                errs += validate_foreign_keys(rows, fks, master_indexes)

            # date range checks
            date_fields = [h for h in headers if "date" in h.lower()]
            if "historical" in rel.lower():
                dr = rules["datasets"]["historical"]
                errs += validate_date_range(rows, dr["start_date"], dr["end_date"], date_fields)
            if "current" in rel.lower():
                dr = rules["datasets"]["current"]
                errs += validate_date_range(rows, dr["start_date"], dr["end_date"], date_fields)

            if errs:
                all_errors.append(f"\n[{entity}] File: {rel}")
                all_errors.extend(errs)

    if all_errors:
        print("\n".join(all_errors))
        raise SystemExit(1)

    print("✅ Validation passed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["generate-prompts", "validate"])
    args = parser.parse_args()

    if args.command == "generate-prompts":
        cmd_generate_prompts()
    else:
        cmd_validate()