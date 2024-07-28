from playwright.sync_api import sync_playwright
from slugify import slugify
import os.path
import json, io


def write_the_json_file(data, name):
    with io.open(f"output/{name}.json", "r+") as file:
        file_data = json.load(file)
        file_data.append(data)
        file.seek(0)
        json.dump(file_data, file, indent=4)


def process(city):
    total = 1000000

    slug = check_file_json_exists(city)

    with sync_playwright() as p:
        search_for = f'cafe di {city}'

        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(000)

        print(f"----- Searching {search_for}".strip())

        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.wait_for_timeout(2000)

        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

        previously_counted = 0
        while True:
            page.mouse.wheel(0, 10000)
            page.wait_for_timeout(3000)

            data = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]')

            if (data.count() >= total):
                listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                listings = [listing.locator("xpath=..") for listing in listings]
                page.locator(
                    '//button[@jsaction="focus:zoom.onZoomInFocus;mouseover:zoom.onZoomInPointerIn;zoom.onZoomInClick;keydown:zoom.keydownAndRipple;ptrdown:ripple.play;mousedown:ripple.play"]').click(
                    click_count=15)
                print(f"Total Scraped: {len(listings)}")
                break
            else:
                if (data.count() == previously_counted):
                    listings = data.all()
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                    break
                else:
                    previously_counted = data.count()
                    print(f"Currently Scrapped: ", data.count())

        page.locator(
            '//button[@jsaction="focus:zoom.onZoomInFocus;mouseover:zoom.onZoomInPointerIn;zoom.onZoomInClick;keydown:zoom.keydownAndRipple;ptrdown:ripple.play;mousedown:ripple.play"]').click(
            click_count=15)
        page.wait_for_timeout(2000)

        for listing in listings:
            try:

                listing.click()
                page.wait_for_timeout(2000)

                nameAttr = listing.locator('//div[contains(@class, "fontHeadlineSmall")]')
                categoryAttr = page.locator('//button[contains(@jsaction, "category")]')
                addressAttr = page.locator('//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]')
                phoneAttr = page.locator(
                    '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]')
                imgs = page.locator(
                    '//button[contains(@jsaction, "heroHeaderImage")]//img[@decoding="async"]').get_attribute('src')

                openingHours = {}
                openHours = page.locator('//table[contains(@class, "fontBodyMedium")]//tbody//tr')
                if openHours.count() > 0:
                    for day in range(openHours.count()):
                        days = openHours.nth(day).locator('//td')
                        for open in range(2):
                            hari = days.nth(open).locator('//div')
                            harinya = None
                            if hari.count() > 0:
                                harinya = hari.all()[0].inner_text()

                            jam = days.nth(open).locator('//ul//li')
                            if jam.count() > 0:
                                jamnya = jam.all()[0].inner_text()
                                if '–' in jamnya:
                                    split = jamnya.split('–')
                                    openingHours[day] = {
                                        "time": {
                                            "open": split[0],
                                            "close": split[1]
                                        }
                                    }
                                else:
                                    openingHours[day] = {
                                        "time": jamnya
                                    }

                page.mouse.click(button='right', x=1211, y=403)
                page.wait_for_timeout(2000)
                latLong = page.locator(
                    '//div[@jsaction="keydown:actionmenu.keydown; contextmenu:actionmenu.contextmenu"]')

                if latLong.count() > 0:
                    dataGeo = latLong.all()[0].inner_text()
                    dataGeo = dataGeo.split("\n")
                    dataGeo = dataGeo[0].split(", ")
                    geo = {
                        "latitude": dataGeo[0],
                        "longitude": dataGeo[1]
                    }
                else:
                    geo = ''

                if nameAttr.count() > 0:
                    name = nameAttr.all()[0].inner_text()
                else:
                    name = ''

                if phoneAttr.count() > 0:
                    phone = phoneAttr.all()[0].inner_text()
                else:
                    phone = ''

                if addressAttr.count() > 0:
                    address = addressAttr.all()[0].inner_text()
                else:
                    address = ''

                if categoryAttr.count() > 0:
                    category = categoryAttr.all()[0].inner_text()
                else:
                    category = ''

                resultJson = {
                    "name": name,
                    "category": category,
                    "address": address,
                    "thumbnail": imgs,
                    "phone": phone,
                    "geo": geo,
                    "openHours": openingHours
                }
                write_the_json_file(resultJson, slug)
                print(f"Processed : {name}")

            except Exception as e:
                print(f"Error occured: {e}")


def check_file_json_exists(city):
    slug = slugify(city)
    check = os.path.isfile(f"output/{slug}.json")
    if not check:
        fp = io.open(f"output/{slug}.json", "w")
        fp.write('[]')
    return slug


def main():
    with io.open(f"cities.json", 'r') as file:
        cities = json.load(file)
        for city in cities:
            slug = slugify(city)
            check = os.path.isfile(f"output/{slug}.json")
            if not check:
                process(city)


if __name__ == "__main__":
    main()
