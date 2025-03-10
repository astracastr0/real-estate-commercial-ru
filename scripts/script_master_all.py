import subprocess
import pandas as pd
import os
import datetime  # Add this import statement
import time  # Import the time module


def run_script_master_for_areas(areas, api_key, script_master_path, output_directory):
    combined_df = pd.DataFrame()
    
    for area in areas:
        current_date = datetime.datetime.now().strftime("%y%m%d")
        enriched_output_csv = os.path.join(output_directory, f'csv_{area}/output_enriched_{area}_{current_date}.csv')

        # Construct and run the command for script_master.py
        command = f'/usr/local/bin/python3 {script_master_path} {area} --api_key {api_key}'
        subprocess.run(command, check=True, shell=True)

        # Pause for 5 minutes to avoid hitting API quota limits
       # print(f"Pausing for 4 minutes to avoid hitting API quota limits...")
       # time.sleep(240)  # Pause for 4 minutes

        # After script_master.py finishes, read the enriched CSV for the area
        if os.path.exists(enriched_output_csv):
            df = pd.read_csv(enriched_output_csv)
            df['Area'] = area  # Optionally add a column to denote the area
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Save the combined DataFrame to a CSV file
    combined_csv_path = os.path.join(output_directory, f'combined_enriched_output_{current_date}.csv')
    combined_df.to_csv(combined_csv_path, index=False)
    print(f"Combined CSV file saved to {combined_csv_path}")

if __name__ == "__main__":
    areas = [   'NAO', 'CAO','VAO', 'ZAO', 'SAO','SZAO', 'SVAO', 'UVAO', 'UAO',  'UZAO','ZelAO']
    #  
    api_key = 'AIzaSyD3uB5Syh7E-tW0a9qLu2EHJ1MqHxqyUu8'  # Replace with your actual API key
    script_master_path = 'scripts/script_master.py'  # Adjust the path to your script_master.py
    output_directory = 'output/csv'  # Directory where the combined CSV should be saved

    run_script_master_for_areas(areas, api_key, script_master_path, output_directory)
