#!/bin/bash

python3 roadnet.py --city $cityname

python3 flow.py --city $cityname --north $north --south $south --east $east --west $west

# $OUTPUT_PATH 由 k8s生成worker时指定
python3 run_simulation.py --output_path $OUTPUT_PATH