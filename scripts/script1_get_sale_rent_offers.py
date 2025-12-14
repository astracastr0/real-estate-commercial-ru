import argparse
import os
import requests
import json
from json import JSONDecodeError
import time

# Define the mappings for districts and undergrounds
districts_undergrounds_mapping = {
       "NAO": {
            "districts": [325,327,328, 329,330, 331,332, 333, 334, 335,336,337],
            "undergrounds": [23,25,136,138,284,285,364,365,366,367,377,378,380],
            "output_folder_sale": "json_files_sale_NAO",
            "output_folder_rent": "json_files_rent_NAO"

        },
    "CAO": {
            "districts": [4,13,14,15,16,17,18,19,20,21,22],
            "undergrounds": [8 ,12,13,15 ,20 ,38 ,46 ,47 ,50  ,53 ,54 ,55 ,56 ,58 ,61 ,64  ,68 ,70 ,71 ,77 ,78 ,80 ,84  ,85 ,86 ,95 ,96 ,98 ,101 ,103    ,105    ,107    ,108    ,110    ,114    ,115    ,117    ,118    ,119    ,121 ,123    ,124    ,125    ,129    ,130    ,132    ,134    ,143 ,145    ,148    ,149    ,150    ,151    ,155    ,159    ,236 ,237    ,272    ,310    ,311    ,384    ,386    ,400    ,425    ,426    ,441    ,470    ,520    ,],
            "output_folder_sale": "json_files_sale_CAO",
            "output_folder_rent": "json_files_rent_CAO"
        },
     "VAO": {
            "districts": [7,70,56,57,59,60,61,62,63,64,65,67,68,69,70,71],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_VAO",
            "output_folder_rent": "json_files_rent_VAO"
        },
    "ZAO": {
            "districts": [11,112,113,114,115,116,117,118,119,120,121,122,123,124,348,349,350],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_ZAO",
            "output_folder_rent": "json_files_rent_ZAO"
        },
    "SAO": {
            "districts": [5,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_SAO",
            "output_folder_rent": "json_files_rent_SAO"
        },
    "SZAO": {
            "districts": [125,126,127,128,129,130,131,132],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_SZAO",
            "output_folder_rent": "json_files_rent_SZAO"
        },
    "SVAO": {
            "districts": [6,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_SVAO",
            "output_folder_rent": "json_files_rent_SVAO"
        },
    "UVAO": {
            "districts": [8,72,73,74,75,76,77,78,79,80,81,82,83],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_UVAO",
            "output_folder_rent": "json_files_rent_UVAO"
        },
    "UAO": {
            "districts": [9,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_UAO",
            "output_folder_rent": "json_files_rent_UAO"
        },
    "UZAO": {
            "districts": [10,100,101,102,103,104,105,106,107,108,109,110,111],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_UZAO",
            "output_folder_rent": "json_files_rent_UZAO"
        },
    "ZelAO": {
            "districts": [151,152,153,154,355,356,357,358],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_ZelAO",
            "output_folder_rent": "json_files_rent_ZelAO"
        },
    "TAO": {
            "districts": [326,338,339,340,341,342,343,344,345,346,347],
            "undergrounds": [],
            "output_folder_sale": "json_files_sale_TAO",
            "output_folder_rent": "json_files_rent_TAO"
        },
        # Add more mappings as needed
    }
# Create a session with requests to avoid repeated connections
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,fr;q=0.8,ru;q=0.7",
    "Referer": "https://www.cian.ru/",
       "bh":"EkIiSGVhZGxlc3NDaHJvbWUiO3Y9IjE0MyIsICJDaHJvbWl1bSI7dj0iMTQzIiwgIk5vdCBBKEJyYW5kIjt2PSIyNCIqAj8wOgcibWFjT1MiYLzx/MkGaiHcytG2Abvxn6sE+taGzAjS0e3rA/y5r/8H3/2HuwXzgQI="
}

session = requests.Session()


def fetch_data_with_retries(json_data, url, max_attempts=5, initial_delay=5):
    attempt = 0
    delay = initial_delay
    session = requests.Session()
    session.headers.update(headers)

    while attempt < max_attempts:
        try:
            print(f"Attempt {attempt + 1}: sending POST request to {url}")
            response = session.post(url, json=json_data, timeout=30)
            if "text/html" in response.headers.get("Content-Type", ""):
                  print("Received HTML (captcha page). Skipping...")
                  
                  print("curl -X POST '{}' \\".format(url))
                  print("-H 'Content-Type: application/json' \\")
                  print("-H 'User-Agent: Mozilla/5.0' \\")
                  print("-d '{}'".format(json.dumps(json_data)))

                  print("Response (first 100 chars):", response.text[:100])
                  return None

            if response.status_code == 429:
                print(f"HTTP 429 Too Many Requests. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
                attempt += 1
                continue

            if response.status_code != 200:
                print(f"HTTP error {response.status_code}")
                print("Response text (first 500 chars):")
                print(response.text[:500])
                return None

            if not response.text.strip():
                print("Empty response body received")
                attempt += 1
                time.sleep(delay)
                delay *= 2
                continue

            try:
                return response.json()
            except JSONDecodeError:
                print("Response is not valid JSON")
                print("Response text (first 500 chars):")
                print(response.text[:500])
                attempt += 1
                time.sleep(delay)
                delay *= 2
                continue

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2
            attempt += 1

    print("Max retries reached. Skipping request.")
    return None


def process_offers(input_parameter, offer_type, base_json_data, output_folder_sale, output_folder_rent):
    """Fetch data from Cian API and process it with retry logic."""
    config = districts_undergrounds_mapping.get(input_parameter)
    if not config:
        raise ValueError(f"Invalid area parameter: {input_parameter}")

    districts = config["districts"]
    undergrounds = config["undergrounds"]

    # Ensure output directories exist
    os.makedirs(output_folder_sale, exist_ok=True)
    os.makedirs(output_folder_rent, exist_ok=True)

    output_folder = output_folder_sale if offer_type == "sale" else output_folder_rent
    api_url = "https://api.cian.ru/commercial-search-offers/desktop/v1/offers/get-offers/"

    for district in districts:
        print(f"Fetching {offer_type} offers for district {district}...")

        district_json_data = base_json_data.copy()
        district_json_data['jsonQuery']['geo'] = {'type': 'geo', 'value': [{'id': district, 'type': 'district'}]}

        data = fetch_data_with_retries(district_json_data, api_url)
        if data:
            filename = f"{output_folder}/output_{offer_type}_district_{district}.json"
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Saved {offer_type} data for district {district}")

        time.sleep(5)  # Avoid rate limits

    for underground in undergrounds:
        print(f"Fetching {offer_type} offers near underground {underground}...")

        underground_json_data = base_json_data.copy()
        underground_json_data['jsonQuery']['geo'] = {'type': 'geo', 'value': [{'id': underground, 'type': 'underground'}]}

        data = fetch_data_with_retries(underground_json_data, api_url)
        if data:
            filename = f"{output_folder}/output_{offer_type}_underground_{underground}.json"
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Saved {offer_type} data for underground {underground}")

        time.sleep(5)  # Avoid rate limits

def main(input_parameter, api_key=None, sale_output_dir=None, rent_output_dir=None):
    """Main function to process sale and rent offers using requests."""
    config = districts_undergrounds_mapping.get(input_parameter)
    if not config:
        raise ValueError(f"Invalid area parameter: {input_parameter}")

    if sale_output_dir is None or rent_output_dir is None:
        raise ValueError("Output directories for sale and rent data must be specified.")

    base_json_data_sale = {
        'jsonQuery': {
            '_type': 'commercialsale',
            'engine_version': {'type': 'term', 'value': 2},
            'office_type': {'type': 'terms', 'value': [2, 5]},
            'region': {'type': 'terms', 'value': [1, 4593]},
            'specialty_types': {'type': 'terms', 'value': [7030, 7037]},
            'is_first_floor': {'type': 'term', 'value': True},
            'publish_period': {'type': 'term', 'value': 604800},  # 1 week
        }
    }

    base_json_data_rent = {
        'jsonQuery': {
            '_type': 'commercialrent',
            'engine_version': {'type': 'term', 'value': 2},
            'office_type': {'type': 'terms', 'value': [2, 5]},
            'region': {'type': 'terms', 'value': [1, 4593]},
            'specialty_types': {'type': 'terms', 'value': [7030, 7037]},
            'is_first_floor': {'type': 'term', 'value': True},
            'publish_period': {'type': 'term', 'value': 2592000},  # 1 month
        }
    }

    print(f"Running script for area: {input_parameter}, API Key: {api_key}")
    print(f"Saving sale data to: {sale_output_dir}")
    print(f"Saving rent data to: {rent_output_dir}")

    process_offers(input_parameter, "sale", base_json_data_sale, sale_output_dir, rent_output_dir)
    process_offers(input_parameter, "rent", base_json_data_rent, sale_output_dir, rent_output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch real estate offers from Cian API.")
    parser.add_argument("input_parameter", type=str, help="Area parameter (e.g., NAO, CAO)")
    parser.add_argument("--api_key", type=str, required=False, help="API key for authentication")
    parser.add_argument("--sale_output_dir", type=str, required=True, help="Directory to save sale JSON files")
    parser.add_argument("--rent_output_dir", type=str, required=True, help="Directory to save rent JSON files")
    args = parser.parse_args()

    main(args.input_parameter, args.api_key, args.sale_output_dir, args.rent_output_dir)
