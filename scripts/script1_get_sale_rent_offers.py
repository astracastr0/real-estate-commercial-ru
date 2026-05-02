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

STATIC_BH = "EkAiTm90KEE6QnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjE0NCIsICJHb29nbGUgQ2hyb21lIjt2PSIxNDQiGgNhcm0iDjE0NC4wLjc1NTkuMTEwKgI/MDoHIm1hY09TIkIGMTMuNC4wSgI2NFJaIk5vdChBOkJyYW5kIjt2PSI4LjAuMC4wIiwiQ2hyb21pdW0iO3Y9IjE0NC4wLjc1NTkuMTEwIiwiR29vZ2xlIENocm9tZSI7dj0iMTQ0LjAuNzU1OS4xMTAiYLeQ08wGaiHcytG2Abvxn6sE+taGzAjS0e3rA/y5r/8H3/373AfzgQI="

# Plan B: fallback cookies from a real browser session (.cian.ru + www.cian.ru)
FALLBACK_COOKIES = {
    "bh": STATIC_BH,
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


async def _make_request_context(playwright, cookie_str, proxy=None):
    """Create a request context with given cookies."""
    kwargs = {
        "extra_http_headers": {
            **HEADERS_BASE,
            "Cookie": cookie_str
        }
    }
    proxy_dict = _parse_proxy(proxy)
    if proxy_dict:
        kwargs["proxy"] = proxy_dict
    return await playwright.request.new_context(**kwargs)


async def _test_api(request_context):
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
    response = await request_context.post(API_URL, data=json.dumps(test_payload))
    text = await response.text()
    if response.status == 200 and not text.startswith("<"):
        return True
    return False


STEALTH_JS = """
// Hide navigator.webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Mock navigator.plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
        { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
    ],
});

// Mock navigator.languages
Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en'] });

// Mock chrome.runtime
window.chrome = { runtime: {} };

// Patch permissions.query
const origQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (params) =>
    params.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : origQuery(params);

// Override WebGL vendor/renderer
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(param) {
    if (param === 37445) return 'Intel Inc.';
    if (param === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, param);
};
"""

STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-infobars",
    "--ignore-certificate-errors",
    "--window-size=1920,1080",
]


async def _visit_cian_stealth(playwright, proxy=None):
    """Launch a stealth browser, visit cian.ru with human-like behavior, return cookie string."""
    launch_opts = {"headless": True, "args": STEALTH_ARGS}
    proxy_dict = _parse_proxy(proxy)
    if proxy_dict:
        launch_opts["proxy"] = proxy_dict

    browser = await playwright.chromium.launch(**launch_opts)
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU",
        timezone_id="Europe/Moscow",
        user_agent=HEADERS_BASE["User-Agent"],
    )

    await context.add_init_script(STEALTH_JS)

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
    await page.goto("https://www.cian.ru/", wait_until="domcontentloaded")

    # Human-like behavior: scroll and move mouse
    await page.wait_for_timeout(random.randint(1500, 3000))
    await page.mouse.move(random.randint(100, 800), random.randint(200, 600))
    await page.evaluate("window.scrollBy(0, %d)" % random.randint(300, 700))
    await page.wait_for_timeout(random.randint(1000, 2000))
    await page.evaluate("window.scrollBy(0, %d)" % random.randint(-200, -50))
    await page.mouse.move(random.randint(400, 1200), random.randint(100, 500))

    # Wait 5-8 seconds total for cookies to settle
    await page.wait_for_timeout(random.randint(5000, 8000))

    cookies = await context.cookies()
    cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    await browser.close()
    return cookies, cookie_str


async def init_request_context(playwright, proxy=None):
    proxy_label = f" (via proxy {proxy})" if proxy else ""

    # План А: заходим на сайт со stealth, чтобы получить валидные cookies
    for attempt in range(1, 3):
        print(f"Plan A (attempt {attempt}): visiting cian.ru with stealth browser{proxy_label}...")
        try:
            cookies, cookie_str = await _visit_cian_stealth(playwright, proxy)

            rc = await _make_request_context(playwright, cookie_str, proxy)
            if await _test_api(rc):
                print(f"Plan A success: got {len(cookies)} valid cookies from browser.")
                return None, rc

            await rc.dispose()
            print(f"Plan A attempt {attempt} failed (API returned captcha).")
        except Exception as e:
            print(f"Plan A attempt {attempt} error: {e}")

        if attempt < 2:
            wait = random.randint(3, 6)
            print(f"Retrying in {wait}s with fresh browser...")
            await asyncio.sleep(wait)

    print("Plan A failed. Switching to Plan B: static cookies...")

    # План Б: используем захардкоженные cookies
    cookie_str = "; ".join(f"{k}={v}" for k, v in FALLBACK_COOKIES.items())
    rc = await _make_request_context(playwright, cookie_str, proxy)
    if await _test_api(rc):
        print("Plan B success: static cookies work.")
        return None, rc

    await rc.dispose()
    print("Plan B also failed. Proceeding with static cookies anyway...")
    rc = await _make_request_context(playwright, cookie_str, proxy)
    return None, rc


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

async def process_offers(area, offer_type, base_payload, output_dir, proxy=None):
    config = districts_undergrounds_mapping[area]
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser, request_context = await init_request_context(p, proxy)

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
        if browser:
            await browser.close()

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
