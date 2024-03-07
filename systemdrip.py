import json
import os
import datetime
import pandas as pd
import subprocess
from persist_metrics import persist_metrics


os.chdir(os.path.dirname(__file__))

with open('config.json') as f:
    config = json.load(f)


def get_pid(service):
    # $ systemctl show --property=MainPID docker
    # > MainPID=1173
    pid = subprocess.check_output(['systemctl', 'show', '--property=MainPID', service]).decode().split('=')[1].strip()
    return int(pid)

def get_pid_value(pid, pid_property):
    if pid > 0:
        # $ ps -p 1173 -o %mem
        # > %MEM
        # > 1.0
        pid_value = subprocess.check_output(['ps', '-p', str(pid), '-o', pid_property]).decode().split('\n')[1].strip()
        return pid_value
    return ''

def get_service_property(service, property):
    # $ systemctl show --property=MainPID docker
    # > MainPID=1173
    return subprocess.check_output(['systemctl', 'show', '--property', property, service]).decode().split('=', 1)[1].strip()

def is_service(service):
    # $ systemctl cat docker.service
    # > *UNIT FILE CONTENTS*
    try:
        subprocess.check_output(['systemctl', 'cat', f'{service}.service'], stderr=subprocess.STDOUT).decode().strip()
        return True
    except:
        return False


# Extract
entries = []
for service in config['services']:
    entry = {}
    entry['Name'] = service

    if not is_service(service):
        entry['Found'] = '-'
        entries.append(entry)
        continue

    entry['Found'] = 'Yes'

    for property in config['properties']:
        entry[property] = get_service_property(service, property)

    for pid_property in config['pid_properties']:
        if pid_property in ['%cpu', '%mem']:
            pid = get_pid(service)
            pid_value = get_pid_value(pid, pid_property)
            if pid_value:
                entry[pid_property] = pid_value

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

df = df[config['final_column_order']]




# Load
with open('systemdrip.html', 'w') as f:
    if 'ActiveState' in df.columns:
        
        def highlight_states(states):
            return ['background-color: #51aa51' if val == 'active' else 'background-color: #c40000' for val in states]
        
        f.write(df.style.apply(highlight_states, subset=['ActiveState']).to_html())
    else:
        f.write(df.to_html())


with open('meta.json', 'w') as f:
    json.dump({'last_updated': datetime.datetime.now().strftime('%b %d, %Y %H:%M:%S')}, f)


if bool(config['persist_metrics']) and all([x in df.columns for x in ['ActiveState', 'MemoryCurrentMB', 'CPUUsageSeconds']]):
    for i, row in df.iterrows():
        persist_metrics(row['Name'], row['ActiveState'], row['MemoryCurrentMB'], row['CPUUsageSeconds'])


print(df.to_string())
