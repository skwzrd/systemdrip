from flask import Flask, render_template
import os
import json
from datetime import datetime
import sqlite3
import pandas as pd

os.chdir(os.path.dirname(__file__))


def get_config():
    with open('config.json') as f:
        config = json.load(f)
    return config

app = Flask(__name__, template_folder='.')


def fetch_persistent_metrics():
    config = get_config()

    conn = sqlite3.connect("systemdrip.db")
    query = "SELECT *, datetime(timestamp, ?) as timestamp_local FROM systemdrip WHERE ROWID % ? = 0 and timestamp > DATE('now', ?) order by timestamp desc limit ?;"
    
    utc_offset_hours = str(get_utc_diff_hours()) + ' hours'
    plot_n_days = '-' + str(int(config['plot_n_days'])) + ' days'
    plot_nth_points = config['plot_nth_points']
    
    limit = len(config['services']) * int(config['plot_n_points_per_service'])

    df = pd.read_sql_query(query, conn, params=[utc_offset_hours, plot_nth_points, plot_n_days, limit])
    return df


def get_utc_diff_hours():
    utc_now = datetime.utcnow()
    local_now = datetime.now()
    offset = local_now - utc_now
    offset_hours = round(offset.total_seconds() / 3600)
    return offset_hours


@app.route('/')
def index():
    config = get_config()

    output_filename_html = 'systemdrip.html'
    output_filename_meta = 'meta.json'
    
    last_update_mins = None
    systemdrip_table = None
    if os.path.isfile(output_filename_html) and os.path.isfile(output_filename_meta):
        with open(output_filename_meta, 'r') as f:
            d_meta = json.load(f)
            last_updated_datetime = datetime.strptime(d_meta["last_updated"], '%b %d, %Y %H:%M:%S')
            last_update_mins = round((datetime.now() - last_updated_datetime).total_seconds() / 60, 1)

        with open(output_filename_html, 'r') as f:
            systemdrip_table = f.read()

    memory_data = None
    cpu_data = None
    if config['chartjs']:
        
        df = fetch_persistent_metrics()
        services = df['service'].unique()

        memory_data = []
        cpu_data = []
        for service in services:
            df_service = df[df['service'] == service].rename(columns={'timestamp_local': 't', 'memory_current_mb': 'm', 'cpu_usage_seconds': 'c'})
            memory_data.append({
                'l': service,
                'd': df_service[['t', 'm']].to_dict(orient='records')
            })
            cpu_data.append({
                'l': service,
                'd': df_service[['t', 'c']].to_dict(orient='records')
            })

    return render_template('server.jinja', config=config, d_meta=d_meta, systemdrip_table=systemdrip_table, last_update_mins=last_update_mins, memory_data=memory_data, cpu_data=cpu_data)

if __name__ == '__main__':
    config = get_config()
    app.run(host=config['host'], port=int(config['port']), debug=bool(config['debug']))
