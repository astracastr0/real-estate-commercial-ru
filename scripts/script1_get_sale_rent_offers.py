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

STATIC_BH = "EkIiSGVhZGxlc3NDaHJvbWUiO3Y9IjE0MyIsICJDaHJvbWl1bSI7dj0iMTQzIiwgIk5vdCBBKEJyYW5kIjt2PSIyNCIqAj8wOgcibWFjT1MiYLzx/MkGaiHcytG2Abvxn6sE+taGzAjS0e3rA/y5r/8H3/2HuwXzgQI="

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Origin": "https://www.cian.ru",
    "Referer": "https://www.cian.ru/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/138.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
}

# =========================
# AREA CONFIG
# =========================

districts_undergrounds_mapping = {
    "NAO": {
        "districts": [325, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337],
        "undergrounds": [],
    },
    "CAO": {
        "districts": [4, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
        "undergrounds": [],
    },
    # остальные округа без изменений
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
