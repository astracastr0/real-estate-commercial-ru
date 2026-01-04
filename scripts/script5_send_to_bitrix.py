import pandas as pd
import requests
import argparse
import json
import logging

BITRIX_URL = "https://doverent.bitrix24.ru/rest/11/c7bky2wft98csftj/crm.item.add?entityTypeId=1032"


def send_to_bitrix_from_csv(csv_path):
    df = pd.read_csv(csv_path)

    # если колонки нет — создаём
    if "bitrix_id" not in df.columns:
        df["bitrix_id"] = None

    for idx, row in df.iterrows():
        # если уже отправляли — пропускаем
        if pd.notna(row.get("bitrix_id")):
            continue

        try:
            # ---------- title ----------
            okrug_raw = str(row.get("geo_okrug", "")).strip()
            okrug_clean = okrug_raw.split(" ")[0] if " (" in okrug_raw else okrug_raw
            raion_or_poselenie = (
                row["geo_raion"]
                if pd.notna(row.get("geo_raion")) and row["geo_raion"]
                else row.get("geo_poselenie", "")
            )
            title = f"{okrug_clean}, {raion_or_poselenie} ({row['totalArea']} м²)"

            # ---------- расчёты ----------
            price = round(row["price"])
            price_per_m = round(row["price_per_meter"])
            median_per_m_month = round(row["median_price_per_m2_month"])
            annual_rent = median_per_m_month * 12
            payback_years = round(row["median_payback_months"] / 12, 1)
            acceptable_price = round(median_per_m_month * row["totalArea"] * 12 * 8, 1)

            # ---------- город ----------
            oblast = str(row.get("geo_oblast", "")).lower()
            if "москва" in oblast:
                city_id = 1013
            elif "московская область" in oblast or "одинцово" in oblast:
                city_id = 1299
            else:
                city_id = None

            # ---------- этаж ----------
            floor = row.get("floorNumber")
            floors = row.get("floorsCount")
            floor_info = (
                f"{int(floor)}/{int(floors)}"
                if pd.notna(floor) and pd.notna(floors)
                else ""
            )

            # ---------- даты ----------
            creation_iso = pd.to_datetime(row["creationDate"]).strftime(
                "%Y-%m-%dT%H:%M:%S+00:00"
            )
            offer_iso = pd.to_datetime(row["offer_date"]).strftime(
                "%Y-%m-%dT%H:%M:%S+00:00"
            )

            # ---------- НДС ----------
            vat_type = str(row.get("vatType", "")).lower()
            if vat_type == "usn":
                tax_type_value_id = 1495
            elif vat_type == "included":
                tax_type_value_id = 1497
            else:
                tax_type_value_id = None

            tax_value = 0 if pd.isna(row.get("vatPrice")) else row["vatPrice"]

            # ---------- поля Bitrix ----------
            fields = {
                "assignedById": 1,
                "stageId": "DT1032_27:NEW",
                "opened": "N",
                "categoryId": 27,
                "title": title,
                "xmlId": str(row["id"]),
                "XML_ID": str(row["id"]),
                "currencyId": "RUB",
                "opportunity": price,
                "ufCrm9_1733219023950": city_id,
                "ufCrm9_1731916825457": f"{row['geo_address_user']}|{row['geo_lat']};{row['geo_lng']}",
                "ufCrm9_1733218987592": str(row["totalArea"]),
                "ufCrm9_1734010228771": f"{acceptable_price}|RUB",
                "ufCrm9_1733994865000": str(price_per_m),
                "ufCrm9_1733219044503": str(int(annual_rent)),
                "ufCrm9_1734504311555": payback_years,
                "ufCrm9_1733995226170": floor_info,
                "ufCrm9_1745585756737": creation_iso,
                "ufCrm9_1745585743945": offer_iso,
                "ufCrm9_1734504157974": [row["url"]],
                "ufCrm9_1733996637": str(row["description"])[:2500],
                "taxValue": tax_value,
                "ufCrm9_1747037770": tax_type_value_id,
            }

            # удаляем пустые
            fields = {k: v for k, v in fields.items() if v not in [None, "", "nan"]}

            payload = {"fields": fields}

            response = requests.post(BITRIX_URL, json=payload, timeout=30)

            if response.status_code == 200:
                bitrix_id = response.json()["result"]["item"]["id"]
                df.at[idx, "bitrix_id"] = bitrix_id
                logging.info(f"Bitrix ID {bitrix_id} created for CIAN {row['id']}")
            else:
                logging.warning(
                    f"Bitrix error {response.status_code} for CIAN {row['id']}: {response.text}"
                )

        except Exception:
            logging.exception(f"🔥 Error while processing CIAN {row.get('id')}")

    # ВАЖНО: сохраняем CSV с bitrix_id
    df.to_csv(csv_path, index=False)

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_path", required=True)
    args = parser.parse_args()
    send_to_bitrix_from_csv(args.csv_path)
