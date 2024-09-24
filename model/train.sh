#!/bin/bash

# Define your Python script and its parameters
run_name="run_final"
start_date="2023-09-01"
end_date="2024-09-17"

# Run the Python script with parameters
python -m model.main $run_name $start_date $end_date 

# # # Define your pytest command and its parameters
run_name_pytest="--run_name=$run_name"
start_date_pytest="--start_date=$start_date"
end_date_pytest="--end_date=$end_date"

# # # # Run pytest with parameters
# pytest model $run_name_pytest $start_date_pytest $end_date_pytest