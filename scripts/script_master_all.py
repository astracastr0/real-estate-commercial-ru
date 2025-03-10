import subprocess  # Ensure this import is included at the top
import pandas as pd
import os
import datetime  # Add this import statement
import time  # Import the time module
import logging  # For better debugging and logging

# Set up logging
log_file = os.path.join(os.path.dirname(__file__), "script_execution.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

def run_script_master_for_areas(areas, api_key, script_master_path, output_directory):
    combined_df = pd.DataFrame()
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    total_start_time = time.time()  # Start time of the whole script
    logging.info("Starting script execution for all areas")

    for area in areas:
        start_time = time.time()  # Start time for the current region
        current_date = datetime.datetime.now().strftime("%y%m%d")
        enriched_output_csv = os.path.join(output_directory, f'csv_{area}/output_enriched_{area}_{current_date}.csv')

        # Ensure area-specific directory exists
        os.makedirs(os.path.dirname(enriched_output_csv), exist_ok=True)

        # Construct and run the command for script_master.py
        command = f'/usr/local/bin/python3 {script_master_path} {area} --api_key {api_key}'
        logging.info(f"Running script for region: {area}")
        
        try:
            subprocess.run(command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing script for region {area}: {e}")
            continue  # Skip this region and proceed to the next one

        end_time = time.time()  # End time for the current region
        execution_time = round(end_time - start_time, 2)
        logging.info(f"Region {area} processed in {execution_time} seconds")

        # After script_master.py finishes, read the enriched CSV for the area
        if os.path.exists(enriched_output_csv):
            df = pd.read_csv(enriched_output_csv)
            df['Area'] = area  # Optionally add a column to denote the area
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    print("Current column order:", list(combined_df.columns))
    logging.info(f"Final column order: {list(combined_df.columns)}")


    # Save the combined DataFrame to a CSV file
    combined_csv_path = os.path.join(output_directory, f'combined_enriched_output_{current_date}.csv')
    combined_df.to_csv(combined_csv_path, index=False)
    logging.info(f"📁 Combined CSV file saved to {combined_csv_path}")

    total_end_time = time.time()  # End time for the whole script
    total_execution_time = round(total_end_time - total_start_time, 2)
    logging.info(f"🎉 Script completed in {total_execution_time} seconds")

if __name__ == "__main__":
    areas = ['NAO', 'CAO', 'VAO', 'ZAO', 'SAO', 'SZAO', 'SVAO', 'UVAO', 'UAO', 'UZAO', 'ZelAO']

    api_key = 'AIzaSyD3uB5Syh7E-tW0a9qLu2EHJ1MqHxqyUu8'  # Replace with your actual API key
    script_master_path = 'scripts/script_master.py'  # Adjust the path to your script_master.py
    output_directory = 'output/csv'  # Directory where the combined CSV should be saved

    run_script_master_for_areas(areas, api_key, script_master_path, output_directory)
