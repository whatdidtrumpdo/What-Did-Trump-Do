import requests
import os 
from flask import Flask
from dotenv import load_dotenv

NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"

def get_news_articles(query, lang='en', page_size=5):
    params = {
        "q": query,
        "language": lang,
        "pageSize": page_size,
        "apiKey": os.getenv("NEWS_API_KEY"),
        "sortBy": "relevancy"
    }
    try:
        response = requests.get(NEWS_API_BASE_URL, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors
        articles = response.json().get('articles', [])
        # Concatenate titles and descriptions for Gemini
        combined_news = "\n\n".join([f"Title: {a['title']}\nDescription: {a['description']}" for a in articles if a['title'] and a['description']])
        return combined_news
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from NewsAPI: {e}")
        return ""