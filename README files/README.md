
# AI-Driven Decision Support Systems for Personalized and Transparent Stock Market Analysis

## Overview of the Project

The stock market is a fast-changing and complex environment. Many people invest their money in stocks, but making the right decisions is difficult. Stock prices change based on many factors such as news, social media, global events, and investor behavior. Predicting these price changes is challenging because the market is highly uncertain and affected by both data and human emotions. Predicting these changes is challenging due to the dynamic and non-linear nature of the market

Many current systems for stock analysis have important limitations. First, most stock prediction models are “black boxes.” They use deep learning or other complex methods but do not explain how a prediction is made. This lack of transparency makes users distrust the system.Explainable AI (XAI) is a growing area that helps solve this by making models easier to understand .

Second, most trading bots only use price data and ignore important signals like social media or financial news. Third, detecting fraud in trading patterns is mostly done by humans or requires labeled data. This takes time and effort, and some scams go unnoticed. Lastly, portfolio recommendation tools often give the same suggestions to everyone without understanding a person’s risk level or financial behavior.

These problems can lead to bad investment decisions, lack of trust in AI systems, and financial losses. There is a strong need for smart systems that are not only accurate but also transparent, personalized, and able to detect problems early.

Our research project aims to address these issues by developing four AI-based components:
• A stock price predictor with explainable AI.
• A sentiment-based trading bot using NLP.
• A fraud detection system using unsupervised learning.
• A personalized portfolio recommendation system based on user risk.

Each part solves a real problem in today’s stock market tools and brings a new feature not commonly found in existing solutions. This will help investors make smarter, safer, and more personalized decisions using AI.

## Project Architectural Diagram

<img width="2119" height="1568" alt="image" src="https://github.com/user-attachments/assets/46e603b4-b8d3-4602-84b8-50d228647cb1" />


## Dependencies List 

## Frontend Dependencies

    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",                 
    "chart.js": "^4.3.0",              
    "react-chartjs-2": "^5.2.0",       
    "tailwindcss": "^3.4.0",          
    "clsx": "^1.2.1",                  
    "react-router-dom": "^6.14.2"   

## Backend Dependencies

fastapi,
uvicorn[standard],
pandas,
numpy,
scipy,
scikit-learn,
torch,
tensorflow,
transformers,
openai,
yfinance,
praw,
tweepy,
requests,
pymongo,
sqlalchemy,
python-dotenv,
python-dateutil,
nltk,
spacy,
loguru,
weaviate-client,
celery[redis],
