from flask import Flask
import os
import json
from datetime import datetime
import sqlite3
import pandas as pd

os.chdir(os.path.dirname(__file__))

with open('config.json') as f:
    config = json.load(f)


app = Flask(__name__)


def fetch_persistent_metrics():
    conn = sqlite3.connect("systemdrip.db")
    query = "SELECT * FROM systemdrip;"
    df = pd.read_sql_query(query, conn)
    return df


@app.route('/')
def index():
    html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2"></script>
            <script src="https://cdn.jsdelivr.net/npm/moment@2.30.1"></script>
            <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@1.0.1"></script>
            <link rel="shortcut icon" href="data:image/x-icon;," type="image/x-icon"> 
            <title>systemdrip</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                table {
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
            <h2>SystemDrip</h2>
            
            <BODY>

            <CHARTS>

            <p>View source code on <a href="https://github.com/skwzrd/systemdrip">GitHub</a></p>
            <script>
                setInterval(function() {
                    location.reload();
                }, 1000 * 60 * 1); // page will reload every 1 minute(s)

                var memoryChartDatasets = <DATA_MEMORY>;
                var cpuChartDatasets = <DATA_CPU>;

                plot_2d('memoryChart', memoryChartDatasets, 'memory_current_mb');
                plot_2d('cpuChart', cpuChartDatasets, 'cpu_usage_seconds');

                function plot_2d(id, chartDataset, col){
                    if(chartDataset){
                        var chartCtx = document.getElementById(id).getContext('2d');
                        var chart = new Chart(chartCtx, {
                            type: 'line',
                            data: {
                                datasets: chartDataset.map(dataset => ({
                                    label: dataset.label,
                                    data: dataset.data.map(entry => ({ x: entry.timestamp, y: entry[col] }))
                                }))
                            },
                            options: {
                                scales: {
                                    x: {
                                        type: 'time',
                                    }
                                }
                            },
                        });
                    }
                }
            </script>
        </body>
        </html>
    """

    output_filename_html = 'systemdrip.html'
    output_filename_meta = 'meta.json'
    body = '<p>Metrics uninitialized. Has <code>python3 systemdrip.py</code> ran yet?</p>'
    if os.path.isfile(output_filename_html) and os.path.isfile(output_filename_meta):
        with open(output_filename_meta, 'r') as f:
            d = json.load(f)
            last_updated_datetime = datetime.strptime(d["last_updated"], '%b %d, %Y %H:%M:%S')
            difference_in_minutes = round((datetime.now() - last_updated_datetime).total_seconds() / 60, 1)
            body = f'<p>Last Updated: {difference_in_minutes} mins ago</p>'

        with open(output_filename_html, 'r') as f:
            body += f.read()

    if config['persist_metrics']:
        charts = """
        <h2>Memory Usage</h2>
        <canvas id="memoryChart" style="max-height: 400px; max-width: 80vw;"></canvas>
        <h2>CPU Usage</h2>
        <canvas id="cpuChart" style="max-height: 400px; max-width: 80vw;"></canvas>
        """
        html_content = html_content.replace('<CHARTS>', charts)

        df = fetch_persistent_metrics()
        services = df['service'].unique()

        memory_chart_data = []
        cpu_chart_data = []
        for service in services:
            service_data = df[df['service'] == service]
            memory_chart_data.append({
                'label': service,
                'data': service_data[['timestamp', 'memory_current_mb']].to_dict(orient='records')
            })
            cpu_chart_data.append({
                'label': service,
                'data': service_data[['timestamp', 'cpu_usage_seconds']].to_dict(orient='records')
            })

        html_content = html_content.replace('<DATA_MEMORY>', json.dumps(memory_chart_data))
        html_content = html_content.replace('<DATA_CPU>', json.dumps(cpu_chart_data))

    else:
        html_content = html_content.replace('<CHARTS>', '')
        html_content = html_content.replace('<DATA_MEMORY>', 'null')
        html_content = html_content.replace('<DATA_CPU>', 'null')
        

    html_content = html_content.replace('<BODY>', body)

    return html_content

if __name__ == '__main__':
    app.run(host=config['host'], port=int(config['port']), debug=bool(config['debug']))
