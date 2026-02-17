import argparse
import os
import json
import time
import asyncio
from playwright.async_api import async_playwright
from json import JSONDecodeError

# =========================
# STATIC CONFIG
# =========================

API_URL = "https://api.cian.ru/commercial-search-offers/desktop/v1/offers/get-offers/"

STATIC_BH = "EkAiTm90KEE6QnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjE0NCIsICJHb29nbGUgQ2hyb21lIjt2PSIxNDQiGgNhcm0iDjE0NC4wLjc1NTkuMTEwKgI/MDoHIm1hY09TIkIGMTMuNC4wSgI2NFJaIk5vdChBOkJyYW5kIjt2PSI4LjAuMC4wIiwiQ2hyb21pdW0iO3Y9IjE0NC4wLjc1NTkuMTEwIiwiR29vZ2xlIENocm9tZSI7dj0iMTQ0LjAuNzU1OS4xMTAiYLeQ08wGaiHcytG2Abvxn6sE+taGzAjS0e3rA/y5r/8H3/373AfzgQI="

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Origin": "https://www.cian.ru",
    "Referer": "https://www.cian.ru/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/144.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-mobile": "?0",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
}

# =========================
# AREA CONFIG
# =========================

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

# =========================
# PLAYWRIGHT CORE
# =========================

async def init_request_context(playwright):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()

    # 1. Жёстко ставим bh
    await context.add_cookies([{
        "name": "bh",
        "value": STATIC_BH,
        "domain": ".cian.ru",
        "path": "/",
        "secure": True,
        "httpOnly": False,
        "sameSite": "Lax",
    }])

    page = await context.new_page()

    # 2. Заходим на сайт, чтобы получить валидные cookies
    await page.goto("https://www.cian.ru/")
    await page.wait_for_timeout(4000)

    cookies = await context.cookies()
    cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

    request_context = await playwright.request.new_context(
        extra_http_headers={
            **HEADERS_BASE,
            "Cookie": cookie_str
        }
    )

    return browser, request_context


async def fetch_json(request_context, payload, retries=3, delay=5):
    for attempt in range(1, retries + 1):
        print(f"Attempt {attempt}: POST {API_URL}")
        response = await request_context.post(API_URL, data=json.dumps(payload))

        text = await response.text()

        if response.status != 200:
            print(f"HTTP {response.status}")
            print(text[:300])
            time.sleep(delay)
            continue

        if text.startswith("<"):
            print("HTML detected (captcha). Skipping.")
            return None

        try:
            return json.loads(text)
        except JSONDecodeError:
            print("Invalid JSON, retrying…")
            time.sleep(delay)

    return None

# =========================
# BUSINESS LOGIC
# =========================

async def process_offers(area, offer_type, base_payload, output_dir):
    config = districts_undergrounds_mapping[area]
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser, request_context = await init_request_context(p)

        for district in config["districts"]:
            print(f"Fetching {offer_type} offers for district {district}")

            payload = json.loads(json.dumps(base_payload))
            payload["jsonQuery"]["geo"] = {
                "type": "geo",
                "value": [{"id": district, "type": "district"}]
            }

            data = await fetch_json(request_context, payload)

            if data:
                filename = f"{output_dir}/output_{offer_type}_district_{district}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Saved {filename}")

            await asyncio.sleep(5)

        await request_context.dispose()
        await browser.close()

# =========================
# ENTRYPOINT
# =========================

def main(area, sale_output_dir, rent_output_dir):
    sale_payload = {
        "jsonQuery": {
            "_type": "commercialsale",
            "engine_version": {"type": "term", "value": 2},
            "office_type": {"type": "terms", "value": [2, 5]},
            "region": {"type": "terms", "value": [1, 4593]},
            "specialty_types": {"type": "terms", "value": [7030, 7037]},
            "is_first_floor": {"type": "term", "value": True},
            "publish_period": {"type": "term", "value": 604800},
        }
    }

    rent_payload = {
        "jsonQuery": {
            "_type": "commercialrent",
            "engine_version": {"type": "term", "value": 2},
            "office_type": {"type": "terms", "value": [2, 5]},
            "region": {"type": "terms", "value": [1, 4593]},
            "specialty_types": {"type": "terms", "value": [7030, 7037]},
            "is_first_floor": {"type": "term", "value": True},
            "publish_period": {"type": "term", "value": 2592000},
        }
    }

    asyncio.run(process_offers(area, "sale", sale_payload, sale_output_dir))
    asyncio.run(process_offers(area, "rent", rent_payload, rent_output_dir))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("area")
    parser.add_argument("--sale_output_dir", required=True)
    parser.add_argument("--rent_output_dir", required=True)
    args = parser.parse_args()

    main(args.area, args.sale_output_dir, args.rent_output_dir)
