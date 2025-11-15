# import praw
# import pandas as pd

# def fetch_reddit_posts(client_id, client_secret, user_agent, keywords, subreddits, limit=300):
#     reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
#     posts = []

#     for sub in subreddits:
#         for submission in reddit.subreddit(sub).search(" OR ".join(keywords), limit=limit):
#             posts.append([
#                 submission.title,
#                 submission.selftext,
#                 submission.score,
#                 submission.subreddit.display_name
#             ])

#     df = pd.DataFrame(posts, columns=["title", "text", "upvotes", "subreddit"])
#     df.to_csv("data/reddit_posts.csv", index=False)
#     return df
