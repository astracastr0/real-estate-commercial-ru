import argparse
import os
import json
import time
import random
import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from json import JSONDecodeError

# =========================
# STATIC CONFIG
# =========================

API_URL = "https://api.cian.ru/commercial-search-offers/desktop/v1/offers/get-offers/"

# Old BH (Chrome 144, Feb 2026)
# STATIC_BH = "EkAiTm90KEE6QnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjE0NCIsICJHb29nbGUgQ2hyb21lIjt2PSIxNDQiGgNhcm0iDjE0NC4wLjc1NTkuMTEwKgI/MDoHIm1hY09TIkIGMTMuNC4wSgI2NFJaIk5vdChBOkJyYW5kIjt2PSI4LjAuMC4wIiwiQ2hyb21pdW0iO3Y9IjE0NC4wLjc1NTkuMTEwIiwiR29vZ2xlIENocm9tZSI7dj0iMTQ0LjAuNzU1OS4xMTAiYLeQ08wGaiHcytG2Abvxn6sE+taGzAjS0e3rA/y5r/8H3/373AfzgQI="

# Fresh BH (Chrome 147, May 2026)
STATIC_BH = "EkAiR29vZ2xlIENocm9tZSI7dj0iMTQ3IiwgIk5vdC5BL0JyYW5kIjt2PSI4IiwgIkNocm9taXVtIjt2PSIxNDciGgNhcm0iDjE0Ny4wLjc3MjcuMTAyKgI/MDoHIm1hY09TIkIGMTMuNC4wSgI2NFJaIkdvb2dsZSBDaHJvbWUiO3Y9IjE0Ny4wLjc3MjcuMTAyIiwiTm90LkEvQnJhbmQiO3Y9IjguMC4wLjAiLCJDaHJvbWl1bSI7dj0iMTQ3LjAuNzcyNy4xMDIiYLqV2s8GaiHcytG2Abvxn6sE+taGzAjS0e3rA/y5r/8H3/3vnAzzgQI="

# Old fallback cookies (Feb 2026)
# FALLBACK_COOKIES = {
#     "bh": STATIC_BH,
#     "tmr_lvidTS": "1771358263726",
#     "tmr_lvid": "9e31abe95e274e6185822dd56403ee5d",
#     "sopr_utm": "%7B%22utm_source%22%3A+%22direct%22%2C+%22utm_medium%22%3A+%22None%22%7D",
#     "sopr_session": "e9e40eee326e4524",
#     "session_region_id": "1",
#     "session_main_town_region_id": "1",
#     "login_mro_popup": "1",
#     "cookie_agreement_accepted": "1",
#     "_ym_visorc": "b",
#     "_ym_uid": "1771358267448125848",
#     "_ym_isad": "2",
#     "_ym_d": "1771358267",
#     "_yasc": "9kvgimsiSrcWgD+vwonG2zfBAgOvpoAVIkdtenSMuHkaeBbHBHKgSA10DkMBOaqe",
#     "_gcl_au": "1.1.1120949663.1771358263",
#     "_ga_3369S417EL": "GS2.1.s1771358266$o1$g1$t1771358296$j30$l0$h0",
#     "_ga": "GA1.1.398076801.1771358267",
#     "tmr_detect": "0%7C1771358297436",
#     "domain_sid": "wJoTWOCpFT57G98EToGxH%3A1771358265300",
#     "_spx": "eyJpZCI6IjkyNzc2MzhjLTYzZjktNDVjYS1iNGIzLWVjZTc2ODVlZDBjMyIsInNvdXJjZSI6IiIsImZpeGVkIjp7InN0YWNrIjpbMCw2MTIwMTAzOTRdfX0%3D",
# }

# Fresh fallback cookies (May 2026, Chrome 147)
FALLBACK_COOKIES = {
    "bh": STATIC_BH,
    "_CIAN_GK": "501d1690-6e64-47fd-b72a-1fdde28e27c3",
    "session_region_id": "1",
    "session_main_town_region_id": "1",
    "cookie_agreement_accepted": "1",
    "tmr_lvidTS": "1771358263726",
    "tmr_lvid": "9e31abe95e274e6185822dd56403ee5d",
    "sopr_utm": "%7B%22utm_source%22%3A+%22direct%22%2C+%22utm_medium%22%3A+%22None%22%7D",
    "sopr_session": "e9e40eee326e4524",
    "session_region_id": "1",
    "session_main_town_region_id": "1",
    "login_mro_popup": "1",
    "cookie_agreement_accepted": "1",
    "_ym_visorc": "b",
    "_ym_uid": "1771358267448125848",
    "_ym_isad": "2",
    "_ym_d": "1771358267",
    "_yasc": "9kvgimsiSrcWgD+vwonG2zfBAgOvpoAVIkdtenSMuHkaeBbHBHKgSA10DkMBOaqe",
    "_gcl_au": "1.1.1120949663.1771358263",
    "_ga_3369S417EL": "GS2.1.s1771358266$o1$g1$t1771358296$j30$l0$h0",
    "_ga": "GA1.1.398076801.1771358267",
    "tmr_detect": "0%7C1771358297436",
    "domain_sid": "wJoTWOCpFT57G98EToGxH%3A1771358265300",
    "_spx": "eyJpZCI6IjkyNzc2MzhjLTYzZjktNDVjYS1iNGIzLWVjZTc2ODVlZDBjMyIsInNvdXJjZSI6IiIsImZpeGVkIjp7InN0YWNrIjpbMCw2MTIwMTAzOTRdfX0%3D",
}

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Origin": "https://www.cian.ru",
    "Referer": "https://www.cian.ru/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/147.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
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
            "districts": [325,327,328,329,330,331,332,333,334,335,336,337],
            "undergrounds": [23,25,127,136,138,284,285,364,365,366,367,377,378,379,380,406,434,435,436,437,438,494,495,496,497,498,499,500,502,535,536,538,543,545,546,547,551,552,553,557],
            "output_folder_sale": "json_files_sale_NAO",
            "output_folder_rent": "json_files_rent_NAO"
        },
    "CAO": {
            "districts": [4,13,14,15,16,17,18,19,20,21,22],
            "undergrounds": [4,8,12,13,14,15,18,20,31,33,38,46,47,50,53,54,55,56,58,61,63,64,66,68,70,71,72,77,78,80,84,85,86,95,96,98,101,103,105,107,108,110,114,115,117,118,119,121,123,124,125,129,130,132,134,143,145,148,149,150,151,155,159,236,237,272,310,311,381,384,385,386,395,396,400,425,426,441,446,451,453,470,512,514,515,518,519,520,540],
            "output_folder_sale": "json_files_sale_CAO",
            "output_folder_rent": "json_files_rent_CAO"
        },
     "VAO": {
            "districts": [7,56,57,59,60,61,62,63,64,65,66,67,68,69,70,71],  # +66 Новокосино
            "undergrounds": [1,34,41,53,76,88,89,90,100,107,113,117,137,146,152,153,155,243,298,299,300,301,302,371,372,373,384,385,386,443,470,471,472,473,474,477,478,479,522,523,524,526,531,539],
            "output_folder_sale": "json_files_sale_VAO",
            "output_folder_rent": "json_files_rent_VAO"
        },
    "ZAO": {
            "districts": [11,112,113,114,115,116,117,118,119,120,121,122,123,124,348,349,350],
            "undergrounds": [11,35,46,57,60,62,70,72,87,93,102,115,120,140,141,142,156,228,233,234,272,281,311,337,338,339,361,362,363,364,365,366,391,392,393,394,395,401,402,403,404,419,440,444,447,450,453,498,499,502,503,504,505,506,507,508,509,510,511,532,535,541,548,549,563],
            "output_folder_sale": "json_files_sale_ZAO",
            "output_folder_rent": "json_files_rent_ZAO"
        },
    "SAO": {
            "districts": [5,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38],
            "undergrounds": [9,14,15,28,29,30,36,37,68,71,81,91,97,106,110,116,128,134,286,289,290,291,292,293,294,295,296,311,349,350,351,352,353,354,369,398,399,412,413,414,422,423,424,451,453,457,459,460,461,463,464,465,466,467,514,515,534],
            "output_folder_sale": "json_files_sale_SAO",
            "output_folder_rent": "json_files_rent_SAO"
        },
    "SZAO": {
            "districts": [125,126,127,128,129,130,131,132],
            "undergrounds": [30,57,72,81,94,97,122,133,154,228,233,234,235,244,275,289,290,291,292,311,351,395,396,420,421,422,440,453,460,461,512,558,559,560,562,563],
            "output_folder_sale": "json_files_sale_SZAO",
            "output_folder_rent": "json_files_rent_SZAO"
        },
    "SVAO": {
            "districts": [6,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55],
            "undergrounds": [5,6,10,15,17,21,27,28,37,69,71,78,83,91,107,110,111,128,236,237,286,287,296,297,298,353,384,399,409,410,411,412,413,414,451,454,467,468,515,516,533,534,537],
            "output_folder_sale": "json_files_sale_SVAO",
            "output_folder_rent": "json_files_rent_SVAO"
        },
    "UVAO": {
            "districts": [8,72,73,74,75,76,77,78,79,80,81,82,83],
            "undergrounds": [1,2,22,31,32,34,40,48,55,59,65,67,92,95,101,108,109,126,240,270,271,282,302,303,304,305,370,371,372,373,374,375,376,425,426,427,428,429,439,443,448,449,452,471,472,473,474,475,476,477,478,479,520,521,522],
            "output_folder_sale": "json_files_sale_UVAO",
            "output_folder_rent": "json_files_rent_UVAO"
        },
    "UAO": {
            "districts": [9,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99],
            "undergrounds": [2,7,19,24,26,38,39,40,43,44,45,48,49,52,55,63,73,74,75,82,85,99,101,112,114,131,135,139,144,147,151,157,238,239,240,245,273,274,283,306,307,308,309,387,388,430,431,432,433,445,554,556,565,566,567,568,569,570,571,573],
            "output_folder_sale": "json_files_sale_UAO",
            "output_folder_rent": "json_files_rent_UAO"
        },
    "UZAO": {
            "districts": [10,100,101,102,103,104,105,106,107,108,109,110,111],
            "undergrounds": [3,7,16,19,23,24,25,33,42,51,63,74,75,79,102,104,127,136,138,139,140,156,158,273,274,281,308,309,389,390,391,434,437,438,450,538,541,548,549,550,554,555],
            "output_folder_sale": "json_files_sale_UZAO",
            "output_folder_rent": "json_files_rent_UZAO"
        },
    "ZelAO": {
            "districts": [151,152,153,154,355,356,357,358],
            "undergrounds": [455,456,457],  # Зеленоград-Крюково, Фирсановская, Сходня
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

def _parse_proxy(proxy_str):
    """Parse proxy string into Playwright proxy dict.

    Supports both simple (http://host:port) and authenticated
    (http://user:pass@host:port) formats.
    """
    if not proxy_str:
        return None
    parsed = urlparse(proxy_str)
    proxy_dict = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
    if parsed.username:
        proxy_dict["username"] = parsed.username
    if parsed.password:
        proxy_dict["password"] = parsed.password
    return proxy_dict


async def _make_request_context(playwright, proxy=None):
    """Create a lightweight request context with fallback cookies and proxy.

    No browser needed — just HTTP requests with cookies.
    """
    cookie_str = "; ".join(f"{k}={v}" for k, v in FALLBACK_COOKIES.items())
    kwargs = {
        "extra_http_headers": {
            **HEADERS_BASE,
            "Cookie": cookie_str,
        },
        "ignore_https_errors": True,
    }
    proxy_dict = _parse_proxy(proxy)
    if proxy_dict:
        kwargs["proxy"] = proxy_dict
    return await playwright.request.new_context(**kwargs)


async def _test_api(rc):
    """Make a test API call to check if cookies are valid. Returns True if OK."""
    test_payload = {
        "jsonQuery": {
            "_type": "commercialsale",
            "engine_version": {"type": "term", "value": 2},
            "office_type": {"type": "terms", "value": [2]},
            "region": {"type": "terms", "value": [1]},
            "geo": {"type": "geo", "value": [{"id": 9, "type": "district"}]}
        }
    }
    response = await rc.post(API_URL, data=json.dumps(test_payload))
    text = await response.text()
    if response.status == 200 and not text.startswith("<"):
        return True
    return False


async def init_request_context(playwright, proxy=None):
    """Create request context with fallback cookies. Returns (None, rc)."""
    proxy_label = f" (via proxy {proxy})" if proxy else ""
    print(f"Initializing API request context with static cookies{proxy_label}...")

    rc = await _make_request_context(playwright, proxy)

    if await _test_api(rc):
        print("API test passed — cookies are valid.")
        return None, rc

    print("API test failed (captcha). Proceeding with static cookies anyway...")
    return None, rc


async def fetch_json(rc, payload, retries=3, delay=5):
    """POST to CIAN API using request context (no browser)."""
    for attempt in range(1, retries + 1):
        print(f"Attempt {attempt}: POST {API_URL}")
        try:
            response = await rc.post(API_URL, data=json.dumps(payload))
            text = await response.text()
        except Exception as e:
            print(f"Connection error: {e}, retrying…")
            await asyncio.sleep(delay)
            continue

        if response.status != 200:
            print(f"HTTP {response.status}")
            print(text[:300])
            await asyncio.sleep(delay)
            continue

        if text.startswith("<"):
            print("HTML detected (captcha). Skipping.")
            return None

        try:
            return json.loads(text)
        except JSONDecodeError:
            print("Invalid JSON, retrying…")
            await asyncio.sleep(delay)

    return None

# =========================
# BUSINESS LOGIC
# =========================

async def process_offers(area, offer_type, base_payload, output_dir, proxy=None):
    config = districts_undergrounds_mapping[area]
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        _, rc = await init_request_context(p, proxy)

        for district in config["districts"]:
            print(f"Fetching {offer_type} offers for district {district}")

            payload = json.loads(json.dumps(base_payload))
            payload["jsonQuery"]["geo"] = {
                "type": "geo",
                "value": [{"id": district, "type": "district"}]
            }

            data = await fetch_json(rc, payload)

            if data:
                filename = f"{output_dir}/output_{offer_type}_district_{district}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Saved {filename}")

            await asyncio.sleep(5)

        for underground in config.get("undergrounds", []):
            print(f"Fetching {offer_type} offers for underground {underground}")

            payload = json.loads(json.dumps(base_payload))
            payload["jsonQuery"]["geo"] = {
                "type": "geo",
                "value": [{"id": underground, "type": "underground"}]
            }

            data = await fetch_json(rc, payload)

            if data:
                filename = f"{output_dir}/output_{offer_type}_underground_{underground}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Saved {filename}")

            await asyncio.sleep(5)

        await rc.dispose()

# =========================
# ENTRYPOINT
# =========================

def main(area, sale_output_dir, rent_output_dir, proxy=None):
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

    asyncio.run(process_offers(area, "sale", sale_payload, sale_output_dir, proxy))
    asyncio.run(process_offers(area, "rent", rent_payload, rent_output_dir, proxy))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("area")
    parser.add_argument("--sale_output_dir", required=True)
    parser.add_argument("--rent_output_dir", required=True)
    parser.add_argument("--proxy", type=str, default=None, help="HTTP proxy, e.g. http://1.2.3.4:8080")
    args = parser.parse_args()

    main(args.area, args.sale_output_dir, args.rent_output_dir, args.proxy)
