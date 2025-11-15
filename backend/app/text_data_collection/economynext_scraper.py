import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_economynext_articles(base_url="https://economynext.com/category/companies/"):
    articles = []
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")

    for item in soup.find_all("article"):
        title_tag = item.find("h3")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        link = item.find("a")["href"]
        date = item.find("time")["datetime"] if item.find("time") else "N/A"

        article_page = requests.get(link)
        article_soup = BeautifulSoup(article_page.text, "html.parser")
        paragraphs = article_soup.find_all("p")
        text = " ".join([p.text for p in paragraphs])

        articles.append([date, title, text, link])

    df = pd.DataFrame(articles, columns=["date", "title", "text", "url"])

    # save inside data folder
    df.to_csv("app/text_data_collection/data/economynext_articles.csv", index=False)
    return df
