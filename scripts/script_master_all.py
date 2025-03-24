import subprocess 
import pandas as pd
import os
import datetime 
import time
import logging
import sys

# Configs
areas = ['NAO']
#, 'CAO', 'VAO', 'ZAO', 'SAO', 'SZAO', 'SVAO', 'UVAO', 'UAO', 'UZAO', 'ZelAO']

api_key = 'AIzaSyD3uB5Syh7E-tW0a9qLu2EHJ1MqHxqyUu8'
script_master_path = 'scripts/script_master.py'
output_directory = 'output'
output_directory_csv = f'{output_directory}/CSV'
to_email = 'fedora121@gmail.com'

# Set up logging
os.makedirs(output_directory, exist_ok=True)
log_file = os.path.join(output_directory, "execution.log")
#logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

file_handler = logging.FileHandler(log_file)
stream_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[file_handler, stream_handler]
    )


def run_for_all_areas(areas, api_key, script_master_path):
    logging.info("Running scripts for all areas")
    total_start_time = time.time() 

    for area in areas:
        command = f'{sys.executable} {script_master_path} {area} --api_key {api_key}'
        
        start_time = time.time()  # Start time for the current region
        logging.info(f"Running script for region: {area}")
        try:
            subprocess.run(command, shell=True, check=True)
        
        except subprocess.CalledProcessError as e:
            logging.error(f"Error processing {area}: {e}")
            continue  # Skip this region and proceed to the next one

        end_time = time.time()  # End time for the current region
        execution_time = round((end_time - start_time)/60, 2)
        logging.info(f"Region {area} processed in {execution_time} min")

    total_end_time = time.time()  # End time for all areas
    total_execution_time = round((total_end_time - total_start_time)/60, 2)
    logging.info(f"Areas parsing completed in {total_execution_time} min")


def run_script_master_for_areas(areas, api_key, script_master_path, output_directory_csv):
    combined_df = pd.DataFrame()
    
    # Ensure output directory exists
    os.makedirs(output_directory_csv, exist_ok=True)

    total_start_time = time.time()  # Start time of the whole script
    logging.info("Starting script execution for all areas")

    for area in areas:
        start_time = time.time()  # Start time for the current region
        current_date = datetime.datetime.now().strftime("%y%m%d")
        enriched_output_csv = os.path.join(output_directory_csv, f'CSV_{area}/output_enriched_{area}_{current_date}.csv')

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

        
def combine_csvs(areas, output_directory_csv):
    combined_df = pd.DataFrame()
    today = datetime.datetime.now().strftime('%y%m%d')

    for area in areas:
        file_path = os.path.join(output_directory_csv, f'CSV_{area}/output_enriched_{area}_{today}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['Area'] = area
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Apply desired column order
    desired_columns = ['id', 'url', 'geo_oblast', 'geo_okrug', 'geo_raion', 'geo_poselenie', 'geo_metro', 'geo_address_user', 'totalArea', 'buildYear', 'houseFinishDate1', 'isFinished', 'floorsCount', 'price', 'price_per_meter', 'vatPrice', 'vatType', 'median_price_per_m2_month', 'median_payback_months', 'offer_date', 'creationDate', 'geo_lng', 'geo_lat', 'description', 'jkUrl', 'geo_jk', 'officeType', 'category', 'layout', 'user_name', 'basicProfiScore', 'isPro', 'dealType', 'pricePerUnitAreaPerYearRur', 'priceTotalPerMonthRur', 'vatPriceTotalPerMonthRur', 'geo_okrug_id', 'geo_raion_id', 'geo_poselenie_id', 'userId', 'photo_full_urls', 'photo_thumbnailUrls', 'photo_thumbnail2Urls', 'rent_offers', 'num_rent_offers', 'min_price_per_m2_month', 'max_price_per_m2_month', 'avg_price_per_m2_month', 'max_payback_months', 'min_payback_months', 'avg_payback_months', 'total_stores_in_1km', 'pharmacy_n', 'liquor_store_n', 'Area']


    if 'median_payback_months' in combined_df.columns:
        combined_df['median_payback_months'] = pd.to_numeric(combined_df['median_payback_months'], errors='coerce')
        combined_df = combined_df[combined_df['median_payback_months'] <= 105]
        logging.info("Applied filter: median_payback_months <= 105")
    else:
        logging.warning("Column 'median_payback_months' not found. Skipping payback filter.")


    combined_df = combined_df[[col for col in desired_columns if col in combined_df.columns]]

    combined_path = os.path.join(output_directory_csv, f'combined_enriched_output_{today}.csv')
    combined_df.to_csv(combined_path, index=False)
    logging.info(f"Combined CSV saved to {combined_path}")
    return combined_df, combined_path


def filter_new_listings(combined_df, output_directory_csv, combined_path=None):
    if 'id' not in combined_df.columns:
        logging.warning("'id' column not found — cannot filter new listings.")
        return None

    if not combined_path:
        today = datetime.datetime.now().strftime('%y%m%d')
        combined_path = os.path.join(output_directory_csv, f'combined_enriched_output_{today}.csv')

    prev_file = os.path.join(output_directory_csv, 'latest.csv')
    diff_file = os.path.join(output_directory_csv, 'new_listings.csv')

    logging.info(f"Rows in current combined_df: {len(combined_df)}")

    cold_start = False

    if os.path.exists(prev_file):
        try:
            prev_df = pd.read_csv(prev_file)
            if prev_df.empty or 'id' not in prev_df.columns:
                logging.warning("⚠atest.csv is empty or malformed. Treating all rows as new.")
                cold_start = True
        except Exception as e:
            logging.warning(f"Error reading latest.csv: {e}. Treating all as new.")
            cold_start = True
    else:
        logging.info("No previous file found — cold start.")
        cold_start = True

    if cold_start:
        new_df = combined_df.copy()
    else:
        new_df = combined_df[~combined_df['id'].isin(prev_df['id'])]
        logging.info(f"New rows after filtering: {len(new_df)}")

    if not new_df.empty:
        diff_file = os.path.join(output_directory_csv, 'new_listings.xlsx')
        new_df.to_excel(diff_file, index=False)


        combined_df.to_csv(prev_file, index=False)
        logging.info(f"New listings saved to {diff_file}")
        return diff_file
    else:
        logging.info("No new listings to send.")
        return None

def filter_unique_new_ids(combined_df, output_directory_csv):
    seen_ids_path = os.path.join(output_directory_csv, "seen_ids.csv")
    diff_file = os.path.join(output_directory_csv, "new_listings.xlsx")

    if "id" not in combined_df.columns:
        logging.warning("'id' column not found — cannot filter new listings.")
        return None

    # 1. Загрузим известные id
    if os.path.exists(seen_ids_path):
        try:
            seen_df = pd.read_csv(seen_ids_path, dtype={"id": str})
            known_ids = set(seen_df["id"].dropna().astype(str))
            logging.info(f"Loaded {len(known_ids)} known IDs")
        except Exception as e:
            logging.error(f"Failed to read seen_ids.csv: {e}")
            known_ids = set()
    else:
        logging.info("No seen_ids.csv found. Starting fresh.")
        known_ids = set()

    # 2. Приведём id к строке для стабильного сравнения
    combined_df["id"] = combined_df["id"].astype(str)
    new_df = combined_df[~combined_df["id"].isin(known_ids)]

    logging.info(f"Found {len(new_df)} truly new listings")

    # 3. Если есть новые — сохраняем и обновляем seen_ids
    if not new_df.empty:
        new_df.to_excel(diff_file, index=False)

        # Обновим базу seen_ids
        updated_ids = pd.Series(list(known_ids | set(new_df["id"])))
        updated_ids_df = pd.DataFrame({"id": updated_ids})
        updated_ids_df.to_csv(seen_ids_path, index=False)

        logging.info(f"Saved {len(new_df)} new listings to {diff_file}")
        return diff_file
    else:
        logging.info("No new listings — all already seen.")
        return None




def send_email_with_file(file_path, to_email):
    logging.info("Preparing to send email...")
    try:
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        count = len(df)
    except Exception as e:
        logging.error(f"Failed to read file for subject line: {e}")
        count = 0
    

    # Формируем заголовок: дата в формате «24 марта»
    months = {
        "01": "января", "02": "февраля", "03": "марта", "04": "апреля",
        "05": "мая", "06": "июня", "07": "июля", "08": "августа",
        "09": "сентября", "10": "октября", "11": "ноября", "12": "декабря"
    }
    now = datetime.datetime.now()
    day = now.strftime("%d").lstrip("0")
    month = months[now.strftime("%m")]
    readable_date = f"{day} {month}"

    subject = f"CIAN, {readable_date}: {count} новых объектов"

    command = (
        f'{sys.executable} scripts/send_email_sendgrid.py '
        f'--to_email {to_email} '
        f'--file_name {os.path.basename(file_path)} '
        f'--subject "{subject}"   '
        f'--body "Новые объявления во вложении."'
    )

    
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Email sent to {to_email} with file {file_path}, subject: {subject}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to send email: {e}")


if __name__ == "__main__":
    # CONTROL SWITCHES
    run_parts = {
        "run_areas": True,
        "combine": True,
        "delta": True,
        "send": True
        }

    combined_df, new_file_path = None, None

    if run_parts["run_areas"]:
        run_for_all_areas(areas, api_key, script_master_path)

    if run_parts["combine"]:
        combined_df, _ = combine_csvs(areas, output_directory_csv)

    if combined_df is None:
        today = datetime.datetime.now().strftime('%y%m%d')
        combined_path = os.path.join(output_directory_csv, f'combined_enriched_output_{today}.csv')
        if os.path.exists(combined_path):
            combined_df = pd.read_csv(combined_path)
            logging.info(f"Loaded combined_df from {combined_path}")
        else:
            logging.error(f"Combined CSV not found at {combined_path}")


    if run_parts["delta"] and combined_df is not None:
        new_file_path = filter_unique_new_ids(combined_df, output_directory_csv)


    if run_parts["send"] and new_file_path:
        send_email_with_file(new_file_path, to_email)
