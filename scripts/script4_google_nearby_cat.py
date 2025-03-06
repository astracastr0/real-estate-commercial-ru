import pandas as pd
import requests
from geopy.distance import geodesic

def fetch_nearby_stores(lat, lng, api_key):
    """Fetch names of nearby stores using Google Places API and categorize them based on specific rules for each type."""
    
    def categorize_store_by_type(store_name, store_type):
        """Categorize store based on its type and name."""
        if store_type == "grocery_or_supermarket":
            if "Magnit" in store_name:
                return "Magnit"
            elif any(pyat in store_name for pyat in ["Pyaterochka", "Pyatorochka", "Pyatyorochka"]):
                return "Pyaterochka"
            elif "Perekrestok" in store_name or "Перекрёсток" in store_name:
                return "Perekrestok"
            else:
                return "Other Grocery"
        elif store_type == "pharmacy":
            if "Apteka" in store_name:
                return "Apteka"
            else:
                return "Other Pharmacy"

    def fetch_stores_by_type(store_type):
        base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": 1000,
            "type": store_type,
            "key": api_key
        }
        response = requests.get(base_url, params=params)
        categorized_stores = {}

        if response.status_code == 200:
            results = response.json().get("results", [])
            for result in results:
                store_name = result["name"]
                category = categorize_store_by_type(store_name, store_type)
                categorized_stores[category] = categorized_stores.get(category, 0) + 1

        return categorized_stores

    # Fetch and categorize stores by type
    grocery_stores = fetch_stores_by_type("grocery_or_supermarket")
    pharmacies = fetch_stores_by_type("pharmacy")
    liquor_stores = fetch_stores_by_type("liquor_store")

    return {
        "grocery_cat": grocery_stores,
        "total_stores_in_1km": sum(grocery_stores.values()),  # Fixed column name
        "pharmacy_cat": pharmacies,
        "pharmacy_n": sum(pharmacies.values()),
        "liquor_store_cat": liquor_stores,
        "liquor_store_n": sum(liquor_stores.values())
    }

def enrich_dataset(csv_path, api_key, output_csv_path):
    df = pd.read_csv(csv_path)

    # Check if the DataFrame is empty
    if df.empty:
        print("Input CSV is empty. No data to process.")
        df.to_csv(output_csv_path, index=False)
        print(f"Empty output CSV saved to {output_csv_path}")
        return  

    # Apply the fetch_nearby_stores function and expand the returned dictionary into separate DataFrame columns
    nearby_stores_info = df.apply(lambda row: fetch_nearby_stores(row["geo_lat"], row["geo_lng"], api_key), axis=1)
    stores_info_df = pd.json_normalize(nearby_stores_info)
    enriched_df = pd.concat([df, stores_info_df], axis=1)

    # Ensure required columns exist before filtering
    required_columns = ["total_stores_in_1km", "pharmacy_n", "liquor_store_n"]
    for col in required_columns:
        if col not in enriched_df.columns:
            print(f"Warning: Column '{col}' is missing in the dataset. Skipping filtering.")
            enriched_df.to_csv(output_csv_path, index=False)
            print(f"Saved enriched dataset (without filtering) to {output_csv_path}")
            return

    # Filtering: Remove records where total stores < 20
    filtered_df = enriched_df[(enriched_df['total_stores_in_1km'] < 20) | 
                              (enriched_df['pharmacy_n'] == 0) | 
                              (enriched_df['liquor_store_n'] == 0)]

    # Save the filtered result
    filtered_df.to_csv(output_csv_path, index=False)
    print(f"Enriched and filtered dataset saved to {output_csv_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Enrich real estate data with Google Places API.')
    parser.add_argument('--api_key', type=str, required=True, help='Google API Key')
    parser.add_argument('--input_csv_path', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--output_csv_path', type=str, required=True, help='Path for the output enriched CSV file')

    args = parser.parse_args()

    enrich_dataset(args.input_csv_path, args.api_key, args.output_csv_path)
