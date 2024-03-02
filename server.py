from flask import Flask
import os
import json

os.chdir(os.path.dirname(__file__))

with open('config.json') as f:
    config = json.load(f)


app = Flask(__name__)

@app.route('/')
def index():
    html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
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

            <p>View source code on <a href="https://github.com/skwzrd/systemdrip">GitHub</a></p>
            <script>
                setInterval(function() {
                    location.reload();
                }, 1000 * 60 * 1); // page will reload every 1 minute(s)
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
            body = f'<p>Last Updated: {d["last_updated"]}</p>'

        with open(output_filename_html, 'r') as f:
            body += f.read()

    html_content = html_content.replace('<BODY>', body)

    return html_content

if __name__ == '__main__':
    app.run(host=config['host'], port=config['port'], debug=config['debug'])
