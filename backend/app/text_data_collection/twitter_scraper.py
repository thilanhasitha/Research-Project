import snscrape.modules.twitter as sntwitter
import pandas as pd
import os



def fetch_tweets(stock_symbols, limit=50):
    all_tweets = []

    for symbol in stock_symbols:
        query = f"{symbol} OR {symbol}.N0000 since:2025-10-01 until:2025-11-12"

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= limit:
                break

            all_tweets.append([
                tweet.date,
                tweet.content,
                tweet.user.username,
                symbol
            ])

    df = pd.DataFrame(all_tweets, columns=["date", "text", "user", "symbol"])

    # save inside data folder
    save_path = "app/text_data_collection/data/twitter_data.csv"
    df.to_csv(save_path, index=False)

    return df
