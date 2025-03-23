import sys
import argparse
import datetime
import os

# Ensure the scripts folder is included in Python's module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from script1_get_sale_rent_offers import main as fetch_offers
from script2_rent_readjs import process_rent_jsons as process_rent
from script2_sale_readjs import process_sale_jsons as process_sale
from script3_cian_join_sale_rent import join_sale_rent
from script4_google_nearby_cat import enrich_dataset

def main(area, api_key):
    # Get the current date in YYMMDD format
    current_date = datetime.datetime.now().strftime("%y%m%d")

    # Define file paths and directories
    sale_json_dir = f'output/step1_json_data/json_files_sale_{area}_{current_date}'
    rent_json_dir = f'output/step1_json_data/json_files_rent_{area}_{current_date}'
    output_dir = f'output/CSV/CSV_{area}'
    sale_output_csv = f'{output_dir}/output_sale_{area}_{current_date}.csv'
    rent_output_csv = f'{output_dir}/output_rent_{area}_{current_date}.csv'
    final_output_csv = f'{output_dir}/output_merged_{area}_{current_date}.csv'
    enriched_output_csv = f'{output_dir}/output_enriched_{area}_{current_date}.csv'  # Path for the enriched output CSV file

    # Ensure directories exist before calling scripts
    os.makedirs(sale_json_dir, exist_ok=True)
    os.makedirs(rent_json_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Fetch sale and rent offers (now passing the output directories)
    #fetch_offers(area, api_key, sale_json_dir, rent_json_dir)  # Updated function call

    # Step 2: Process sale and rent offers (script 2 will now use the correct JSON input directories)
    #process_sale(sale_json_dir, sale_output_csv)
    #process_rent(rent_json_dir, rent_output_csv)

    # Step 3: Combine sale and rent data
    #join_sale_rent(sale_output_csv, rent_output_csv, final_output_csv)

    # Step 4: Enrich the combined sale and rent data with nearby store information
    enrich_dataset(final_output_csv, api_key, enriched_output_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch, process, and combine real estate offers.')
    parser.add_argument('area', type=str, help='Area parameter (e.g., NAO, UAO, ZAO)')
    parser.add_argument('--api_key', type=str, required=True, help='Google API key for fetching nearby store information')
    args = parser.parse_args()
    main(args.area, args.api_key)
