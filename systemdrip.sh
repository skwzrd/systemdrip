#!/bin/bash

readarray -t services <<< $(jq -r '.services[]' config.json)
readarray -t properties <<< $(jq -r '.properties[]' config.json)
readarray -t pid_properties <<< $(jq -r '.pid_properties[]' config.json)
data_filename=$(jq -r '.data_filename' config.json)
delimiter=$(jq -r '.delimiter' config.json)

data_filepath="$(dirname $(realpath -s $0))/$data_filename"
> $data_filepath

for service in "${services[@]}"; do

    x=$(systemctl cat "$service.service" 2>&1)
    
    if [[ $x == "No files found"* ]]; then
        echo $x
        echo ""
        continue
    fi

    echo "Name=$service" >> $data_filepath
    for property in "${properties[@]}"; do
        systemctl show --property="$property" "$service" >> $data_filepath
    done

    for pid_property in "${pid_properties[@]}"; do
        if [[ $pid_property == "%cpu" || $pid_property == "%mem" ]]; then
            pid=$(systemctl show --property=MainPID $service | cut -d'=' -f2)
            if [[ $pid -gt 0 ]]; then
                echo "$pid_property=$(ps -p $pid -o $pid_property | sed -n '2p')" >> $data_filepath
            fi
        fi
    done

    if [[ $service != ${services[-1]} ]]; then
        echo $delimiter >> $data_filepath
    fi

done

python3 main.py
