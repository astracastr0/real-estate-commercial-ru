import pandas as pd
import requests
import argparse
import json
import os
import datetime
import logging 

def send_to_bitrix_from_csv(csv_path):
    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():
        try:
            # Prepare 'title'
            okrug_raw = str(row.get("geo_okrug", "")).strip()
            okrug_clean = okrug_raw.split(" ")[0] if " (" in okrug_raw else okrug_raw
            raion_or_poselenie = row["geo_raion"] if pd.notna(row["geo_raion"]) and row["geo_raion"] else row.get("geo_poselenie", "")
            title = f"{okrug_clean}, {raion_or_poselenie} ({row['totalArea']} м²)"

            # Подготовка округлённых чисел
            price = round(row["price"])
            price_per_m = round(row["price_per_meter"])
            median_per_m_month = round(row["median_price_per_m2_month"])
            annual_rent = median_per_m_month * 12
            payback_years = round(row["median_payback_months"] / 12, 1)
            acceptable_price = round(row["median_price_per_m2_month"] * row["totalArea"] * 12 * 8, 1)

            # Город ID
            oblast = str(row.get("geo_oblast", "")).lower()
            if "москва" in oblast:
                city_id = 1013
            elif "московская область" in oblast or "одинцово" in oblast:
                city_id = 1299
            else:
                city_id = None

            # Этаж и этажность
            floor = row.get("floorNumber", "")
            floors = row.get("floorsCount", "")
            floor_info = f"{int(floor)}/{int(floors)}" if pd.notna(floor) and pd.notna(floors) else ""

            # Dates
            creation_iso = pd.to_datetime(row["creationDate"]).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            offer_iso = pd.to_datetime(row["offer_date"]).strftime("%Y-%m-%dT%H:%M:%S+00:00")

            # Налог
            tax_value = 0 if pd.isna(row.get("vatPrice")) else row["vatPrice"]

            # Тип Налога
            vat_type = row.get("vatType", "").lower()
            
            # outdated - tax_type_value = "УСН" if vat_type == "usn" else None

            #tax_type_value_id for custom field "Тип налога" ufCrm9_1747037770, 1495 ->"УСН", "ID":"1497"->"НДС включен"
            if vat_type == "usn":
                tax_type_value_id = 1495 
            elif vat_type == "included":
                tax_type_value_id = 1497 
            else:
                tax_type_value_id = None 

            fields = {
                "assignedById": 1,
                "stageId": "DT1032_27:NEW",
                "opened": "N",
                "categoryId": 27,
                "isManualOpportunity":"N",
                "ufCrm9_1733995107315": 1073,
                "ufCrm9_1733218914289": 1009, 
                "ufCrm9_1734504008856":1191, # размещен на ЦИАН - Да
                "sourceDescription": "CIAN parser",
                "title": title,
                "xmlId": str(row["id"]),
                "currencyId": "RUB",
                "opportunity": price,
                "ufCrm9_1733219023950": city_id,
                "ufCrm9_1731916825457": f"{row['geo_address_user']}|{row['geo_lat']};{row['geo_lng']}",
                "ufCrm9_1733218987592": str(row["totalArea"]),
                "ufCrm9_1734010228771": f"{acceptable_price}|RUB", # Приемлемая цена (расчет 8 лет окупаемости по аренде)
                "ufCrm9_1733994865000": str(price_per_m),
                "ufCrm9_1737107006262": f"{median_per_m_month}|RUB",
                "ufCrm9_1733219044503": str(int(annual_rent)),
                "ufCrm9_1734504311555": payback_years,
                "ufCrm9_1733995226170": floor_info,
                "ufCrm9_1745585756737": creation_iso,
                "ufCrm9_1745585743945": offer_iso,
                "ufCrm9_1734504157974": [row["url"]],
                "ufCrm9_1745581561068": row.get("jkUrl", ""),
                "ufCrm9_1733996637": str(row["description"])[:2500],
                "ufCrm9_1737363589516": f"https://yandex.ru/maps/?text={row['geo_address_user']}",
                "taxValue": tax_value,
                # "ufCrm9_1745581414925": tax_type_value
                "ufCrm9_1747037770": tax_type_value_id
            }

            # Удалить пустые
            fields = {k: v for k, v in fields.items() if v not in [None, "", "nan"]}

            payload = {"fields": fields}
            url = "https://doverent.bitrix24.ru/rest/11/c7bky2wft98csftj/crm.item.add?entityTypeId=1032"
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                json_response = response.json()
                bitrix_id = json_response.get("result", {}).get("item", {}).get("id", "UNKNOWN")
                logging.info(f"Bitrix ID: {bitrix_id}, xmlId: {row['id']}")
            else:
                logging.info(f"Ошибка: {row['id']} — {response.status_code} | {response.text}")

        except Exception as e:
            logging.info(f"Ошибка при обработке ID {row.get('id')}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_path', required=True, help='Path to CSV file with listings')
    args = parser.parse_args()
    send_to_bitrix_from_csv(args.csv_path)
