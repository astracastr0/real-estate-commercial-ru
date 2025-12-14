import asyncio
import json
from playwright.async_api import async_playwright

STATIC_BH = "EkIiSGVhZGxlc3NDaHJvbWUiO3Y9IjE0MyIsICJDaHJvbWl1bSI7dj0iMTQzIiwgIk5vdCBBKEJyYW5kIjt2PSIyNCIqAj8wOgcibWFjT1MiYLzx/MkGaiHcytG2Abvxn6sE+taGzAjS0e3rA/y5r/8H3/2HuwXzgQI="

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # ⬇️ Устанавливаем bh cookie вручную до загрузки страницы
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

        # ⬇️ Заход на сайт, чтобы получить другие cookies (например _CIAN_GK)
        await page.goto("https://www.cian.ru/")
        await page.wait_for_timeout(3000)

        # ⬇️ Собираем все cookies
        cookies = await context.cookies()
        cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

        # ⬇️ Создаём отдельный request context
        request_context = await p.request.new_context(
            base_url="https://api.cian.ru",
            extra_http_headers={
                "Content-Type": "application/json",
                "Origin": "https://www.cian.ru",
                "Referer": "https://www.cian.ru/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept-Language": "ru-RU",
                "X-Requested-With": "XMLHttpRequest",
                "Cookie": cookie_str  # ⬅️ используем актуальную строку cookie
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
        print("Cookies used:", cookie_str)
        text = await response.text()
        print("Text preview:", text[:500])

        try:
            data = json.loads(text)
            print("✅ Response JSON parsed successfully")
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON — possibly a CAPTCHA page or an HTML error")

        await request_context.dispose()
        await browser.close()

asyncio.run(main())

