import json
import os
import datetime
import pandas as pd

# Extract
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)
data_filepath = os.path.join(os.path.dirname(__file__), CONFIG['data_filename'])

entries = []
entry = {}
with open(data_filepath, 'r') as f:
    for line in f:
        line = line.strip()
        if line == CONFIG['delimiter']:
            entries.append(entry)
            entry = {}
        else:
            key, value = [x.strip() for x in line.split("=")]
            entry[key] = value
            
    if entry:
        entries.append(entry)


# Transform
df = pd.DataFrame(entries)

StateChangeTimestamp = pd.to_datetime(df['StateChangeTimestamp'], format="%a %Y-%m-%d %H:%M:%S %Z")
Now = datetime.datetime.now(tz=datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)

df['StateChangeTimestampDeltaSeconds'] = (Now - StateChangeTimestamp).dt.total_seconds()
df['State (Days)']    = round(df["StateChangeTimestampDeltaSeconds"] / 3600 / 24, 1)
df['MemoryCurrentMB'] = round(pd.to_numeric(df['MemoryCurrent'], errors='coerce') / 1024 / 1024, 1)
df['CPUUsageSeconds'] = round(pd.to_numeric(df['CPUUsageNSec'], errors='coerce') / 1e9, 1)
df.fillna(0, inplace=True)


# Load
final_column_order = [
    "Name",
    "ActiveState",
    'State (Days)',
    "MemoryCurrentMB",
    "CPUUsageSeconds"
]
print(df[final_column_order].to_string())
