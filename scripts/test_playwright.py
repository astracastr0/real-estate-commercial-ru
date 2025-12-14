import asyncio
import json
from playwright.async_api import async_playwright

OUTPUT_FILE = "cian_response.json"
CAPTCHA_FILE = "cian_response.html"

STATIC_BH = "EkIiSGVhZGxlc3NDaHJvbWUiO3Y9IjE0MyIsICJDaHJvbWl1bSI7dj0iMTQzIiwgIk5vdCBBKEJyYW5kIjt2PSIyNCIqAj8wOgcibWFjT1MiYLzx/MkGaiHcytG2Abvxn6sE+taGzAjS0e3rA/y5r/8H3/2HuwXzgQI="

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Устанавливаем bh cookie вручную до захода на сайт
        await context.add_cookies([{
            'name': 'bh',
            'value': STATIC_BH,
            'domain': '.cian.ru',
            'path': '/',
            'httpOnly': False,
            'secure': True,
            'sameSite': 'Lax'
        }])

        page = await context.new_page()
        await page.goto("https://www.cian.ru/")
        await page.wait_for_timeout(3000)

        cookies = await context.cookies()
        cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

        request_context = await p.request.new_context(
            base_url="https://api.cian.ru",
            extra_http_headers={
                "Content-Type": "application/json",
                "Origin": "https://www.cian.ru",
                "Referer": "https://www.cian.ru/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept-Language": "ru-RU",
                "X-Requested-With": "XMLHttpRequest",
                "Cookie": cookie_str
            }
        )

        payload = {
            "jsonQuery": {
                "_type": "commercialsale",
                "engine_version": {"type": "term", "value": 2},
                "office_type": {"type": "terms", "value": [2, 5]},
                "region": {"type": "terms", "value": [1, 4593]},
                "specialty_types": {"type": "terms", "value": [7030, 7037]},
                "is_first_floor": {"type": "term", "value": True},
                "publish_period": {"type": "term", "value": 604800},
                "geo": {"type": "geo", "value": [{"id": 327, "type": "district"}]}
            }
        }

        response = await request_context.post(
            "/commercial-search-offers/desktop/v1/offers/get-offers/",
            data=json.dumps(payload)
        )

        print("Status:", response.status)
        text = await response.text()

        try:
            data = json.loads(text)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Response saved to {OUTPUT_FILE}")
        except json.JSONDecodeError:
            # Сохраняем HTML в файл для анализа капчи
            with open(CAPTCHA_FILE, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"❌ Failed to parse JSON — saved HTML to {CAPTCHA_FILE}")

        await request_context.dispose()
        await browser.close()

asyncio.run(main())
