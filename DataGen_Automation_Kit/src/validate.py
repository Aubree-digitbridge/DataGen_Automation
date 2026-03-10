import csv
from pathlib import Path
from typing import Dict, List, Tuple
from dateutil.parser import isoparse

def read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = [r for r in reader]
    return headers, rows

def validate_required(rows: List[Dict[str, str]], required: List[str]) -> List[str]:
    errors = []
    for i, r in enumerate(rows, start=2):
        for field in required:
            if field not in r:
                errors.append(f"Line {i}: required field '{field}' not present in file")
            else:
                if (r[field] is None) or (str(r[field]).strip() == ""):
                    errors.append(f"Line {i}: required field '{field}' is blank")
    return errors

def validate_unique(rows: List[Dict[str, str]], pk_fields: List[str]) -> List[str]:
    if not pk_fields:
        return []
    errors = []
    seen = set()
    for i, r in enumerate(rows, start=2):
        key = tuple((r.get(f, "") or "").strip() for f in pk_fields)
        if any(k == "" for k in key):
            errors.append(f"Line {i}: primary key {pk_fields} contains blank value(s): {key}")
            continue
        if key in seen:
            errors.append(f"Line {i}: duplicate primary key {pk_fields} = {key}")
        seen.add(key)
    return errors

def validate_date_range(rows: List[Dict[str, str]], start_date: str, end_date: str, date_fields: List[str]) -> List[str]:
    errors = []
    start = isoparse(start_date).date()
    end = isoparse(end_date).date()
    for i, r in enumerate(rows, start=2):
        for f in date_fields:
            if f not in r:
                continue
            val = (r.get(f) or "").strip()
            if not val:
                continue
            try:
                d = isoparse(val).date()
                if d < start or d > end:
                    errors.append(f"Line {i}: {f}={val} outside range {start_date}..{end_date}")
            except Exception:
                errors.append(f"Line {i}: {f}={val} is not a valid ISO date (YYYY-MM-DD)")
    return errors

def build_index(rows: List[Dict[str, str]], field: str) -> set:
    return set((r.get(field) or "").strip() for r in rows if (r.get(field) or "").strip())

def validate_foreign_keys(
    child_rows: List[Dict[str, str]],
    fk_map: Dict[str, Dict[str, str]],
    master_indexes: Dict[str, Dict[str, set]]
) -> List[str]:
    errors = []
    for i, r in enumerate(child_rows, start=2):
        for fk_field, ref in fk_map.items():
            val = (r.get(fk_field) or "").strip()
            if not val:
                continue
            ent = ref["entity"]
            fld = ref["field"]
            allowed = master_indexes.get(ent, {}).get(fld, set())
            if allowed and val not in allowed:
                errors.append(f"Line {i}: FK {fk_field}={val} not found in {ent}.{fld}")
    return errors
