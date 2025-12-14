
import asyncio
from playwright.async_api import async_playwright
import json




async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
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
                "User-Agent": "Mozilla/5.0 ...",
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
            data=json.dumps(payload)  # <-- сериализуем вручную
        )
        print("Status:", response.status)
        print("cookies:", cookie_str)
        text = await response.text()
        print("Text preview:", text[:500])

        try:
            data = json.loads(text)
            print("Response JSON:", data)
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON. Possibly HTML or captcha.")

        await request_context.dispose()
        await browser.close()

asyncio.run(main())
