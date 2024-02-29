# SystemDrip

## Running

`./sysdtemdrip.sh`

## Output

```
No files found for not_existent.service.

              Name  State (Days) ActiveState   Result  MemoryCurrentMB  CPUUsageSeconds
0            nginx           0.1      active  success             10.0              0.0
1  qbittorrent-nox           2.0      active  success             11.1             84.2
2           docker           3.6      active  success            102.6             48.7
3              neo           0.0      active  success            161.2             67.2
4      quart_12345           0.0    inactive  success              0.0            112.0
```

## Configuration

Configure the file `config.json` with the following,

- `services`: any service you want to monitor.
- `properties`: any systemd properties you're interested in. View the existing properties and their values for a given service with `sudo systemctl show docker`.
- `pid_properties`: supports `%mem` and `%cpu`.
- `data_filename`: an arbitrary file name. Data is written here for communication between Bash and Python.
- `delimiter`: an arbitrary string that is highly unique.

`sudo chmod +x systemdrip.sh`

## Dependencies

- Python3
- Pandas, `pip install pandas`
- JSON processor, `sudo apt install jq`

## Why

The following Prometheus exporters didn't support this by default.

- https://github.com/prometheus-community/systemd_exporter
- https://github.com/ncabatoff/process-exporter
- https://github.com/prometheus/node_exporter


## Roadmap

- Interface the output from this script to a [text-collector](https://github.com/prometheus/node_exporter?tab=readme-ov-file#textfile-collector).
