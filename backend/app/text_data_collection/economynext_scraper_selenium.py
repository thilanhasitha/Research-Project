import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium_setup import create_driver

BASE_URL = "https://www.economynext.com/markets/page/"

def safe_get(driver, url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            driver.get(url)
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"⚠ Retry {attempt+1}/{retries} failed for {url}: {e}")
            time.sleep(delay)
    return False

def scrape_economynext_dynamic(pages=3):
    driver = create_driver()

    titles, urls, dates, contents = [], [], [], []

    for p in range(1, pages + 1):
        url = f"{BASE_URL}{p}"
        print("Scraping:", url)

        if not safe_get(driver, url):
            continue

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # UPDATED selector
        articles = soup.select("h3.jeg_post_title a")

        print(f"🔎 Found {len(articles)} articles on page {p}")

        for a in articles:
            link = a["href"]
            title = a.get_text(strip=True)

            if not safe_get(driver, link):
                continue

            art = BeautifulSoup(driver.page_source, "html.parser")

            # UPDATED selectors
            content = art.select_one("div.entry-content")
            date = art.select_one("div.jeg_meta_date")

            titles.append(title)
            urls.append(link)
            dates.append(date.get_text(" ", strip=True) if date else "")
            contents.append(content.get_text(" ", strip=True) if content else "")

    driver.quit()

    df = pd.DataFrame({
        "title": titles,
        "date": dates,
        "url": urls,
        "content": contents
    })

    return df
