import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False для отладки
        context = await browser.new_context()
        page = await context.new_page()

        # Зайти на сайт, чтобы получить cookies и session
        await page.goto("https://www.cian.ru/")

        # Можно подождать немного, чтобы точно всё загрузилось
        await page.wait_for_timeout(3000)

        # Выполнить запрос через fetch внутри браузера
        result = await page.evaluate('''async () => {
        const response = await fetch("https://api.cian.ru/commercial-search-offers/desktop/v1/offers/get-offers/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                jsonQuery: {
                    _type: "commercialsale",
                    engine_version: { type: "term", value: 2 },
                    office_type: { type: "terms", value: [2, 5] },
                    region: { type: "terms", value: [1, 4593] },
                    specialty_types: { type: "terms", value: [7030, 7037] },
                    is_first_floor: { type: "term", value: true },  // <-- lowercase "true"
                    publish_period: { type: "term", value: 604800 },
                    geo: { type: "geo", value: [{ id: 327, type: "district" }] }
                }
            })
        });

        if (!response.ok) {
            return { status: response.status, text: await response.text() };
        }

        return await response.json();
    }''')


        print(result)

        await browser.close()

asyncio.run(main())


