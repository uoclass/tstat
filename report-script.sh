#!/bin/bash

# report file - export this from EXCEL with "File -> Save as -> UTF-8 CSV"
report_name="tstat-report-11.csv"

# term parameters - beginning and end of term
start_date="09/27/2024"
end_date="11/01/2024"

# define base query
tstat_base_query="python3 cli.py -t $start_date -e $end_date -l $report_name"

# chart commands to run - please refer to wiki to find out how to write these queries
commands=(
"$tstat_base_query -q perweek"
"$tstat_base_query -q perroom --head 30"
"$tstat_base_query -q perbuilding --head 30"
"$tstat_base_query -q perrequestor --head 30"
"$tstat_base_query -q perdiagnosis"
)

# Loop through each chart command
for cmd in "${commands[@]}"; do
    # Wait for a keypress before running the command
    echo "Press any key to run the next query..."
    read -n 1 -s  # wait for a single key press

    # Run the command
    echo "Running: $cmd"
    $cmd
done

echo "All commands completed."
