from pathlib import Path
import random
import string
import re
from collections import defaultdict, Counter
from datetime import datetime
from openpyxl import load_workbook, Workbook
import csv

base = Path(__file__).resolve().parents[1]
prompt_file = base / 'prompts' / '_daily' / 'Shipment_trackingNumber_prompt.txt'


def parse_prompt_paths(path: Path):
    txt = path.read_text(encoding='utf-8')
    vals = {}
    for line in txt.splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            k = key.strip().upper()
            if k in {'FILE_NAME', 'CHANNEL_ACCOUNT_MAPPING_FILE', 'OUTPUT_FOLDER'}:
                vals[k] = value.strip()
    missing = {'FILE_NAME', 'CHANNEL_ACCOUNT_MAPPING_FILE', 'OUTPUT_FOLDER'} - set(vals)
    if missing:
        raise RuntimeError(f'Missing required prompt constants: {sorted(missing)}')
    return vals


cfg = parse_prompt_paths(prompt_file)
input_file = base / cfg['FILE_NAME']
mapping_file = base / cfg['CHANNEL_ACCOUNT_MAPPING_FILE']
output_folder = base / cfg['OUTPUT_FOLDER']
completed_file = base / 'output' / 'Shipment-Tracking_completed.xlsx'

output_folder.mkdir(parents=True, exist_ok=True)
for old in output_folder.glob('*.xlsx'):
    old.unlink()

mapping = {}
with mapping_file.open('r', encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError('Mapping file is empty')
    cols = list(rows[0].keys())
    lower = {str(c).strip().lower(): c for c in cols}
    key_col = lower.get('channelaccountnum') or lower.get('channel account num') or lower.get('channel_account_num')
    name_col = lower.get('channelaccountname') or lower.get('channel account name') or lower.get('channel_account_name')
    if not key_col or not name_col:
        raise RuntimeError(f'Missing mapping columns. Found: {cols}')
    for r in rows:
        k = str(r.get(key_col) or '').strip()
        v = str(r.get(name_col) or '').strip()
        if k:
            mapping[k] = v if v else k

wb = load_workbook(input_file)
ws = wb.active
headers = [c.value for c in ws[1]]
index = {str(h).strip(): i for i, h in enumerate(headers)}
carrier_col = index.get('Carrier')
track_col = index.get('Tracking Number')
chan_col = index.get('ChannelAccountNum')
channel_col = index.get('Channel')
if channel_col is None:
    channel_col = index.get('channel')
if channel_col is None:
    channel_col = index.get('Channel Name')
if channel_col is None:
    channel_col = index.get('channelName')
order_col = index.get('channelOrderID')
if order_col is None:
    order_col = index.get('Channel Order ID')
if order_col is None:
    order_col = index.get('ChannelOrderID')

required = {
    'Carrier': carrier_col,
    'Tracking Number': track_col,
    'channelOrderID/Channel Order ID': order_col,
}
missing = [k for k, v in required.items() if v is None]
if missing:
    raise RuntimeError(f'Missing required columns: {missing}; headers: {headers}')


def resolve_channel_label(data_row):
    if channel_col is not None:
        channel_value = str(data_row[channel_col] or '').strip()
        if channel_value:
            return channel_value

    channel_account_num = str(data_row[chan_col] or '').strip() if chan_col is not None else ''
    if channel_account_num:
        mapped = mapping.get(channel_account_num, '').strip()
        if mapped:
            return mapped
        return channel_account_num

    return 'UNKNOWN_CHANNEL'


def gen_ups():
    chars = string.ascii_uppercase + string.digits
    return '1Z' + ''.join(random.choice(chars) for _ in range(16))


def gen_fedex():
    return ''.join(random.choice(string.digits) for _ in range(random.choice([12, 15])))


def gen_usps():
    return ''.join(random.choice(string.digits) for _ in range(random.choice([20, 21, 22])))


def gen_dhl():
    return ''.join(random.choice(string.digits) for _ in range(10))


def gen_track(carrier):
    c = str(carrier or '').strip().upper()
    if c == 'FEDEX':
        return gen_fedex()
    if c == 'USPS':
        return gen_usps()
    if c == 'DHL':
        return gen_dhl()
    return gen_ups()

rows = list(ws.iter_rows(min_row=2))
order_groups = defaultdict(list)
for row in rows:
    order_id = str(row[order_col].value or '').strip()
    order_groups[order_id].append(row)

all_existing = set()
for row in rows:
    t = str(row[track_col].value or '').strip()
    if t:
        all_existing.add(t)

filled_orders = 0
propagated_orders = 0
newly_filled_cells = 0

for order_id, group in order_groups.items():
    existing_in_group = []
    for row in group:
        t = str(row[track_col].value or '').strip()
        if t:
            existing_in_group.append(t)

    if existing_in_group:
        chosen = existing_in_group[0]
        if any(x != chosen for x in existing_in_group[1:]):
            raise RuntimeError(f'Conflicting existing tracking numbers within channelOrderID={order_id}')
        for row in group:
            cur = str(row[track_col].value or '').strip()
            if not cur:
                row[track_col].value = chosen
                newly_filled_cells += 1
        propagated_orders += 1
        continue

    carrier = str(group[0][carrier_col].value or '').strip()
    t = gen_track(carrier)
    while t in all_existing:
        t = gen_track(carrier)
    all_existing.add(t)
    for row in group:
        row[track_col].value = t
        newly_filled_cells += 1
    filled_orders += 1

completed_file_written = completed_file
try:
    wb.save(completed_file_written)
except PermissionError:
    completed_file_written = base / 'output' / f"Shipment-Tracking_completed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(completed_file_written)

all_data_rows = [list(r) for r in ws.iter_rows(min_row=2, values_only=True)]
by_channel = defaultdict(list)
for data_row in all_data_rows:
    by_channel[resolve_channel_label(data_row)].append(data_row)

invalid = re.compile(r'[<>:"/\\|?*]')
written_files = []
for channel_name, channel_rows in by_channel.items():
    file_name_base = channel_name if channel_name else 'UNKNOWN_CHANNEL'
    safe_name = invalid.sub('_', file_name_base).strip().rstrip('.') or 'UNKNOWN_CHANNEL'
    out_file = output_folder / f'{safe_name}.xlsx'

    nwb = Workbook()
    nws = nwb.active
    out_headers = [h for i, h in enumerate(headers) if i != chan_col] if chan_col is not None else list(headers)
    nws.append(out_headers)
    for row in channel_rows:
        nws.append([v for i, v in enumerate(row) if i != chan_col] if chan_col is not None else list(row))
    nwb.save(out_file)
    written_files.append(out_file.name)

pat_ups = re.compile(r'^1Z[A-Z0-9]{16}$')
pat_fedex = re.compile(r'^(\d{12}|\d{15})$')
pat_usps = re.compile(r'^\d{20,22}$')
pat_dhl = re.compile(r'^\d{10}$')

bad_format = 0
tracking_values = []
for r in ws.iter_rows(min_row=2, values_only=True):
    carrier = str(r[carrier_col] or '').strip().upper()
    track = str(r[track_col] or '').strip()
    tracking_values.append(track)
    if carrier == 'FEDEX':
        ok = bool(pat_fedex.match(track))
    elif carrier == 'USPS':
        ok = bool(pat_usps.match(track))
    elif carrier == 'DHL':
        ok = bool(pat_dhl.match(track))
    else:
        ok = bool(pat_ups.match(track))
    if not ok:
        bad_format += 1

dups = sum(v - 1 for v in Counter(tracking_values).values() if v > 1)

# order consistency validation
order_tracking_violations = 0
order_channels = defaultdict(set)
order_tracking = defaultdict(set)
for r in ws.iter_rows(min_row=2, values_only=True):
    oid = str(r[order_col] or '').strip()
    ch = resolve_channel_label(r)
    tr = str(r[track_col] or '').strip()
    order_channels[oid].add(ch)
    order_tracking[oid].add(tr)

for oid, ts in order_tracking.items():
    if len(ts) > 1:
        order_tracking_violations += 1

orders_in_multiple_channels = sum(1 for chs in order_channels.values() if len(chs) > 1)

print('prompt_file', prompt_file.as_posix())
print('input_file', input_file.as_posix())
print('mapping_file', mapping_file.as_posix())
print('output_folder', output_folder.as_posix())
print('completed_file', completed_file_written.as_posix())
print('rows_total', len(all_data_rows))
print('orders_total', len(order_groups))
print('orders_with_new_tracking_generated', filled_orders)
print('orders_with_existing_tracking_propagated', propagated_orders)
print('cells_filled', newly_filled_cells)
print('tracking_duplicates_dataset', dups)
print('carrier_format_failures', bad_format)
print('order_tracking_violations', order_tracking_violations)
print('orders_in_multiple_channels', orders_in_multiple_channels)
print('split_files_written', len(written_files))
print('split_files', sorted(written_files))
