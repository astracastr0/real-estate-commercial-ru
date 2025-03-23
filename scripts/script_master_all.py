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
        absolute_script_path = os.path.abspath(script_master_path)
        command = f'python3 {absolute_script_path} {area} --api_key {api_key}'
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
    
    # Define the desired column order
    desired_column_order = ['id', 'url', 'geo_oblast', 'geo_okrug', 'geo_raion', 'geo_poselenie', 'geo_metro', 'geo_address_user', 'totalArea', 'buildYear', 'houseFinishDate1', 'isFinished', 'floorsCount', 'price', 'price_per_meter', 'vatPrice', 'vatType', 'median_price_per_m2_month', 'median_payback_months', 'offer_date', 'creationDate', 'geo_lng', 'geo_lat', 'description', 'jkUrl', 'geo_jk', 'officeType', 'category', 'layout', 'user_name', 'basicProfiScore', 'isPro', 'dealType', 'pricePerUnitAreaPerYearRur', 'priceTotalPerMonthRur', 'vatPriceTotalPerMonthRur', 'geo_okrug_id', 'geo_raion_id', 'geo_poselenie_id', 'userId', 'photo_full_urls', 'photo_thumbnailUrls', 'photo_thumbnail2Urls', 'rent_offers', 'num_rent_offers', 'min_price_per_m2_month', 'max_price_per_m2_month', 'avg_price_per_m2_month', 'max_payback_months', 'min_payback_months', 'avg_payback_months', 'total_stores_in_1km', 'pharmacy_n', 'liquor_store_n', 'Area']

    # Reorder columns if they exist in the dataframe
    combined_df = combined_df[[col for col in desired_column_order if col in combined_df.columns]]

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
