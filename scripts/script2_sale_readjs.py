# example of run: /usr/local/bin/python3 script2_sale_readjs.py --input_dir ./json_files_sale_nao --output_file output_sale_nao_november.csv

import json
import csv
import os
import argparse
from datetime import datetime

def process_sale_jsons(input_directory, output_file):
    # Initialize a dictionary to store offers, keyed by ID
    offers_by_id = {}

    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            
            for item in data["data"]["offersSerialized"]:
                description = item.get("description", "").replace('\n', ' ')

                price_type = item.get("bargainTerms", {}).get("priceType", "")
                total_area = item.get("totalArea", 0)
                total_area = float(total_area) if total_area else 0

                price = item.get("bargainTerms", {}).get("priceRur", 0)
                price = price*total_area if price_type == "squareMeter" else price 
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
                
                geo_jk = next((d["shortName"] for d in item.get("geo", {}).get("address", []) if d.get("locationTypeId") == 213), "")
                jk = geo_jk if geo_jk != "" else item.get("js", {}).get("displayName", "")

                houseFinishDate1 = next((d["text"] for d in item.get("factoids", []) if d.get("type") == "houseFinishDate"), "")
                newbuilding = item.get("newbuilding")
                buildYear = item.get("building", {}).get("buildYear", 0)
                isFinished = ""
                if newbuilding:
                    house = newbuilding.get("house")
                    if house:
                        finishDate = house.get("finishDate")
                        isFinished = house.get("isFinished", "")
                        if finishDate:
                            buildYear = finishDate.get("year", "")

                offer_id = item.get("id", "")
                jk_url = item.get("jkUrl", "").split()[0] if item.get("jkUrl", "") else ""

                photo_fullurl = [photo["fullUrl"] for photo in item.get("photos", [])]
                photo_fullurls = ";".join(photo_fullurl)

                photo_thumbnailUrl = [photo["thumbnailUrl"] for photo in item.get("photos", [])]
                photo_thumbnailUrls = ";".join(photo_thumbnailUrl)

                photo_thumbnail2Url = [photo["thumbnail2Url"] for photo in item.get("photos", [])]
                photo_thumbnail2Urls = ";".join(photo_thumbnail2Url)

                
                # If the ID already exists in the dictionary, append the jkUrl if it's new
                if offer_id in offers_by_id:
                    # Check if the jkUrl is new and not empty, then append it
                    if jk_url and jk_url not in offers_by_id[offer_id]["jkUrl"].split(';'):
                        offers_by_id[offer_id]["jkUrl"] += f";{jk_url}"
                else:
                    # If the ID is new, add the entire offer to the dictionary
                    offers_by_id[offer_id] = {
                        "id": offer_id,
                        # Include other fields as necessary
                        "jkUrl": jk_url,
                        "userId": item.get("userId", ""),
                        "dealType": item.get("dealType", ""),

                        "offer_date": datetime.fromtimestamp(item.get("addedTimestamp", 0)),
                        
                        "creationDate": item.get("creationDate", ""),
                        "officeType": item.get("officeType", ""),
                        "category": item.get("category", ""),
                        "totalArea": item.get("totalArea", 0),
                        "buildYear": buildYear,
                        "floorNumber": floorNumber,
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
                        "houseFinishDate1": houseFinishDate1,
                        "basicProfiScore": item.get("basicProfiScore", 0),
                        "isPro": item.get("basicProfiScore", ""),
                        "isFinished" : isFinished,
                        "photo_full_urls": photo_fullurls,
                        "photo_thumbnailUrls": photo_thumbnailUrls,
                        "photo_thumbnail2Urls": photo_thumbnail2Urls,
                        "user_name": item.get("user", {}).get("agencyName", "")
                       
                    }


    # Write the processed data to a CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["id", "url", "user_name", "geo_oblast", "geo_okrug", "geo_raion", "geo_poselenie", "geo_metro", "geo_address_user",
                        "totalArea", 
                      "buildYear", "houseFinishDate1","isFinished", "floorNumber", "floorsCount", "price", "price_per_meter", 
                      "vatPrice", "vatType", "offer_date", "creationDate",
                       "geo_lng", "geo_lat", "description", 
                      "jkUrl", "geo_jk","officeType", "category","layout", "basicProfiScore", "isPro", 
                      "dealType", 
                      "pricePerUnitAreaPerYearRur", "priceTotalPerMonthRur", 
                      "vatPriceTotalPerMonthRur", "geo_okrug_id", "geo_raion_id", "geo_poselenie_id","userId",
                      "photo_full_urls", "photo_thumbnailUrls", "photo_thumbnail2Urls"
                      ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        for offer_id, offer_details in offers_by_id.items():
            writer.writerow(offer_details)

    print(f"Processed {len(offers_by_id)} unique offers into {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process JSON files and output CSV.')
    parser.add_argument('--input_dir', type=str, help='Directory containing JSON files with sale offers')
    parser.add_argument('--output_file', type=str, help='Output CSV file name for processed sale offers')
    args = parser.parse_args()
    process_sale_jsons(args.input_dir, args.output_file)
