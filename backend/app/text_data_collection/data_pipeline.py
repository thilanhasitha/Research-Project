from app.text_data_collection.twitter_scraper import fetch_tweets
from app.text_data_collection.economynext_scraper import fetch_economynext_articles
import pandas as pd
import os 
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_pipeline():
    print("Starting Sri Lanka Stock Sentiment Data Collection...\n")

    stock_symbols = ["JKH", "LOLC", "HNB", "CARG"]

    # 1. Twitter
    twitter_df = fetch_tweets(stock_symbols)
    print("Twitter collected:", len(twitter_df))

    # 2. EconomyNext
    econ_df = fetch_economynext_articles()
    print("EconomyNext collected:", len(econ_df))

    # 3. Combine
    combined = pd.concat([
        twitter_df.rename(columns={"text": "content"}),
        econ_df.rename(columns={"text": "content"})
    ], ignore_index=True)

    # Export final combined dataset
    combined.to_csv("app/text_data_collection/data/combined_data.csv", index=False)

    print("\nSaved combined_data.csv successfully!")


if __name__ == "__main__":
    run_pipeline()
