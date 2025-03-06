import json
import csv
import os
import argparse
from datetime import datetime

# New function encapsulating the script's functionality
def process_rent_jsons(input_directory, output_file):
    # Initialize a set to store unique offers
    unique_offers = set()

    # Iterate over JSON files in the specified directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)

            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)

                for item in data["data"]["offersSerialized"]:
                    description = item.get("description", "").replace('\n', ' ')

                    price_type = item.get("bargainTerms", {}).get("priceType", "")
                    price_period = item.get("bargainTerms", {}).get("paymentPeriod", "")
                    total_area = item.get("totalArea", 0)
                    total_area = float(total_area) if total_area else 0

                    price = item.get("bargainTerms", {}).get("priceRur", 0)
                    price = price*total_area if price_type == "squareMeter" and price_period != "annual" else price*total_area/12 if price_type == "squareMeter" else price/12 if price_period == "annual"  else price 
                    price_per_meter = price / total_area if total_area > 0 else 0

                    # Extract "raion" and "okrug" from "districts"
                    raion = next((d["name"] for d in item.get("geo", {}).get("districts", []) if d.get("type") == "raion"), "")
                    raion_id = next((d["id"] for d in item.get("geo", {}).get("districts", []) if d.get("type") == "raion"), "")
                    okrug = next((d["name"] for d in item.get("geo", {}).get("districts", []) if d.get("type") == "okrug"), "")
                    okrug_id = next((d["id"] for d in item.get("geo", {}).get("districts", []) if d.get("type") == "okrug"), "")
                    metro = next((d["name"] for d in item.get("geo", {}).get("districts", []) if d.get("type") == "metro"), "")
                    
                    poselenie = next((d["name"] for d in item.get("geo", {}).get("districts", []) if d.get("type") == "poselenie"), "")
                    poselenie_id = next((d["id"] for d in item.get("geo", {}).get("districts", []) if d.get("type") == "poselenie"), "")
                    
                    oblast = next((d["shortName"] for d in item.get("geo", {}).get("address", []) if d.get("locationTypeId") == 2), "")
                    
                    city = next((d["shortName"] for d in item.get("geo", {}).get("address", []) if d.get("locationTypeId") == 1), "")
                    oblast = city if city != "" else oblast
                    
                    jk = next((d["shortName"] for d in item.get("geo", {}).get("address", []) if d.get("locationTypeId") == 213), "")
                    
                    houseFinishDate = next((d["text"] for d in item.get("factoids", []) if d.get("type") == "houseFinishDate"), "")


            
            
                    offer = {
                        "id": item.get("id", ""),
                        "userId": item.get("userId", ""),
                        "dealType": item.get("dealType", ""),

                        "offer_date": datetime.fromtimestamp(item.get("addedTimestamp", 0)),
                        "creationDate": item.get("creationDate", ""),
                        "officeType": item.get("officeType", ""),
                        "category": item.get("category", ""),
                        "totalArea": item.get("totalArea", 0),
                        "jkUrl": item.get("jkUrl", ""),
                        "buildYear": item.get("building", {}).get("buildYear", 0),
                        "floorsCount": item.get("building", {}).get("floorsCount", 0),
                        "url": item.get("fullUrl", ""),
                        "description": description,
                        "price": item.get("bargainTerms", {}).get("priceRur", 0),
                        "price_per_meter": price_per_meter,
                        "geo_lng": item.get("geo", {}).get("coordinates", {}).get("lng", ""),
                        "geo_lat": item.get("geo", {}).get("coordinates", {}).get("lat", ""),
                        "geo_oblast": oblast,
                        "geo_address_user": item.get("geo", {}).get("userInput", ""),
                        "geo_raion": raion,  
                        "geo_okrug": okrug,
                        "geo_raion_id": raion_id,  
                        "geo_okrug_id": okrug_id,
                        "geo_poselenie": poselenie,
                        "geo_poselenie_id": poselenie_id,
                        "geo_metro": metro,
                        "vatPrice": item.get("bargainTerms", {}).get("vatPrice", 0),
                        "vatType": item.get("bargainTerms", {}).get("vatType", ""),
                        "pricePerUnitAreaPerYearRur": item.get("pricePerUnitAreaPerYearRur", 0),
                        "priceTotalPerMonthRur": item.get("priceTotalPerMonthRur", 0),
                        "vatPriceTotalPerMonthRur": item.get("vatPriceTotalPerMonthRur", 0),
                        "layout": item.get("layout", ""),
                        "geo_jk": jk,
                        "houseFinishDate": houseFinishDate,
                        "basicProfiScore": item.get("basicProfiScore", 0),
                        "isPro": item.get("basicProfiScore", "")
                        }
              

                    # Convert the offer dictionary to a tuple for use in the set
                    offer_tuple = tuple(offer.items())

                    # Only add the offer if it's not already in the set
                    if offer_tuple not in unique_offers and price_per_meter <= 100000:
                        unique_offers.add(offer_tuple)

    # Convert the unique offers back to dictionaries
    unique_offers = [dict(offer) for offer in unique_offers]

    # Write the extracted unique data to a CSV file
    delimiter = '|'  # Define the delimiter
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["id", "userId", "dealType", "offer_date", "creationDate", "officeType", "category","totalArea", "layout"
        , "buildYear", "floorsCount", "price", "price_per_meter", "vatPrice", "vatType", "pricePerUnitAreaPerYearRur", "priceTotalPerMonthRur", "vatPriceTotalPerMonthRur", "url", "geo_oblast", "geo_okrug", "geo_okrug_id"
        , "geo_raion", "geo_raion_id", "geo_poselenie_id", "geo_poselenie", "geo_metro",  "geo_address_user", "geo_lng", "geo_lat", "description", "jkUrl"
        , "geo_jk", "houseFinishDate", "basicProfiScore", "isPro"
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        for offer in unique_offers:
            writer.writerow(offer)

    print(f"Data from {len(unique_offers)} JSON files saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process JSON files and output CSV.')
    parser.add_argument('--input_dir', type=str, help='Directory containing JSON files with rent offers')
    parser.add_argument('--output_file', type=str, help='Output CSV file name with rent offers')

    args = parser.parse_args()
    process_rent_jsons(args.input_dir, args.output_file)
