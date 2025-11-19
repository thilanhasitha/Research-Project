import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium_setup import create_driver

def scrape_dailyft_dynamic():
    driver = create_driver()
    driver.get("https://www.ft.lk/business")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # CORRECT selector from your screenshot
    titles_html = soup.select("div.title a")
    dates_html = soup.select("div.posted-on")

    print(f"🔎 Found {len(titles_html)} articles")

    titles, urls, dates, contents = [], [], [], []

    for a, d in zip(titles_html, dates_html):
        link = "https://www.ft.lk" + a["href"]
        title = a.get_text(strip=True)
        date = d.get_text(strip=True)

        driver.get(link)
        time.sleep(2)

        art = BeautifulSoup(driver.page_source, "html.parser")

        # CORRECT article body selector
        body = art.select_one("div.article-content")

        titles.append(title)
        urls.append(link)
        dates.append(date)
        contents.append(body.get_text(" ", strip=True) if body else "")

    driver.quit()

    df = pd.DataFrame({
        "title": titles,
        "date": dates,
        "url": urls,
        "content": contents
    })

    return df
