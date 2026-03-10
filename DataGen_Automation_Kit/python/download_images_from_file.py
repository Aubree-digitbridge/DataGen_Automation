from __future__ import annotations

import csv
import os
from pathlib import Path
from urllib.parse import urlparse, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===== Settings =====
INPUT_FILE = "data/image_urls.csv"   # or: image_urls.csv
DOWNLOAD_DIR = Path("images")
MAX_WORKERS = 30                # choose 20 to 50
TIMEOUT = 30
# ====================


def build_session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=MAX_WORKERS,
        pool_maxsize=MAX_WORKERS,
    )

    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        }
    )
    return session


def filename_from_url(url: str) -> str:
    path = urlparse(url).path
    name = os.path.basename(path)
    return unquote(name) or "downloaded_image.jpg"


def extension_from_url(url: str) -> str:
    name = filename_from_url(url)
    suffix = Path(name).suffix
    return suffix if suffix else ".jpg"


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', "_", name.strip())
    cleaned = cleaned.rstrip(". ")
    return cleaned or "downloaded_image"


def unique_path(base_dir: Path, filename: str) -> Path:
    target = base_dir / filename
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    counter = 1
    while True:
        candidate = base_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def read_items_from_txt(file_path: Path) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url and not url.startswith("#"):
                name = Path(filename_from_url(url)).stem
                items.append((name, url))
    return items


def read_items_from_csv(file_path: Path) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames:
            lowered = {name.lower(): name for name in reader.fieldnames}

            substyle_col = (
                lowered.get("substylecode")
                or lowered.get("substyle")
                or lowered.get("sub_style_code")
                or lowered.get("substyle code")
            )
            basic_attr_col = lowered.get("basicattributevalue")

            if substyle_col and basic_attr_col:
                for row in reader:
                    substyle = (row.get(substyle_col) or "").strip()
                    url = (row.get(basic_attr_col) or "").strip()
                    if substyle and url:
                        items.append((substyle, url))
                return items

            url_col = None
            for candidate in ["url", "image_url", "link"]:
                if candidate in lowered:
                    url_col = lowered[candidate]
                    break

            if url_col:
                for row in reader:
                    url = (row.get(url_col) or "").strip()
                    if url:
                        name = Path(filename_from_url(url)).stem
                        items.append((name, url))
                return items

    # fallback: first column if no header matched
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader2 = csv.reader(f)
        for row in reader2:
            if row and row[0].strip().lower() not in {"url", "image_url", "link", "substyle", "substylecode"}:
                url = row[0].strip()
                if url:
                    name = Path(filename_from_url(url)).stem
                    items.append((name, url))
    return items


def read_items(input_file: str) -> list[tuple[str, str]]:
    path = Path(input_file)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    ext = path.suffix.lower()
    if ext == ".txt":
        return read_items_from_txt(path)
    if ext == ".csv":
        return read_items_from_csv(path)

    raise ValueError("Only .txt and .csv files are supported.")


def download_one(session: requests.Session, file_key: str, url: str) -> tuple[str, bool, str]:
    try:
        response = session.get(url, timeout=TIMEOUT, stream=True)
        response.raise_for_status()

        ext = extension_from_url(url)
        target_name = f"{sanitize_filename(file_key)}{ext}"
        file_path = unique_path(DOWNLOAD_DIR, target_name)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)

        return url, True, str(file_path)
    except Exception as e:
        return url, False, str(e)


def main() -> None:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    items = read_items(INPUT_FILE)
    items = list(dict.fromkeys(items))  # remove exact duplicates while keeping order

    if not items:
        print("No downloadable items found in input file.")
        return

    print(f"Found {len(items)} items in {INPUT_FILE}")
    print(f"Starting download with {MAX_WORKERS} workers...")

    failed: list[tuple[str, str]] = []
    session = build_session()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(download_one, session, name, url) for name, url in items]

        for i, future in enumerate(as_completed(futures), start=1):
            url, ok, result = future.result()
            if ok:
                print(f"[{i}/{len(items)}] OK    {result}")
            else:
                print(f"[{i}/{len(items)}] FAIL  {url} -> {result}")
                failed.append((url, result))

    if failed:
        fail_log = DOWNLOAD_DIR / "failed_downloads.txt"
        with open(fail_log, "w", encoding="utf-8") as f:
            for url, error in failed:
                f.write(f"{url}\nERROR: {error}\n\n")
        print(f"\nCompleted with {len(failed)} failures.")
        print(f"Failure log saved to: {fail_log}")
    else:
        print("\nAll downloads completed successfully.")


if __name__ == "__main__":
    main()