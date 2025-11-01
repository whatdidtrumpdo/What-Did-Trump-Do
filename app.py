# main Flask app file

from flask import Flask, request, jsonify # import Flask which is the web framework
from dotenv import load_dotenv # import load_dotenv to load environment variables
import os # import os to access environment variables
import requests # import requests to make HTTP requests to NewsAPI
import finhub # import finhub-python package to access Finhub API
import pandas as pd # import pandas for data manipulation
import time
import mplfinance as mpf # import mplfinance for financial charting
import google.generativeai as genai
import json

load_dotenv() # load api keys from .env file for security

genai.configure(api_key=os.getenv("GENAI_API_KEY")) # what this does it set the API key for gemini so that we can make requests to the API
model = genai.GenerativeModel('gemini-2.5-pro') # specify the model version to use


def gemini_analysis(news_articles, sector): # takes in news articles and sector as input, might change to take only 1 article later
    prompt = f"""
        Analyze the following news articles about Donal Trump's recent actions and their impact on the
        {sector} sector: Based on this, provide:

        1. Investor Sentiment (Bullish, Bearish, or Neutral) and explain why
        2. Short-Term Market Outlook (Up, Down, Consolidate) and explain why
        3. Long-Term Market Outlook (Up, Down, Consolidate) and explain why
        4. 4 popular example stocks in this sector that are most likely to be affected, along with their predicted short-term movement (e.g., AAPL: Up, GOOG: Consolidate).
        5. A concise, paragraph-long summary suitable for a financial news report and retail investor.

    Format your response strictly as JSON:
    {{
      "sentiment": "...",
      "whySentiment": "...",
      "shortTermOutlook": "...",
      "whyShortTermOutlook": "...",
      "longTermOutlook": "...",
      "whyLongTermOutlook": "...",
      "stocksAffected": [
        {{"ticker": "...", "movement": "..."}},
        {{"ticker": "...", "movement": "..."}},
        {{"ticker": "...", "movement": "..."}},
        {{"ticker": "...", "movement": "..."}}
      ],
      "newsSummary": "..."
    }}

     ---
    News Articles:
    {news_articles}
    """

    try:
        response = model.generate_content(prompt)
        return response.text # returns the generated text from the gemeni model after passing the prompt
    except Exception as e:
        print(f"Error generating text: {e}")
        return None


NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"

def get_news_articles(query, lang='en', page_size=5):
    # sets up parameters that will be sent to NewsAPI to fetch news articles
    params = {
        "q": query, # what to search for
        "language": lang, # language of the news articles
        "pageSize": page_size, # number of articles to fetch
        "apiKey": os.getenv("NEWS_API_KEY"), # use api key from .env file
        "sortBy": "relevancy" # sort articles by relevancy
    }
    try:
        response = requests.get(NEWS_API_BASE_URL, params=params)
        response.raise_for_status() # checks if response has HTTP errors ( 401 or 404 not found), raises exception if so
        articles = response.json().get('articles', []) # gets list of articles (".get()") and converts to python dictionary (.json()) default to empty list if none found
        # Concatenate titles and descriptions for Gemini
        combined_news = "\n\n".join([f"Title: {a['title']}\nDescription: {a['description']}" for a in articles if a['title'] and a['description']]) #  may add more fields later, for more detailed analysis
        return combined_news # returns the combined news articles as a single string separated by 2 new lines
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from NewsAPI: {e}")
        return "" # return empty string on error instead of None because gemini expects a string, otherwise gemini_analysis would crash

def Finhub_charts(): # placeholder for Finhub charts function
    finhub_client = finhub.Client(api_key=os.getenv("FINHUB_API_KEY")) # initialize Finhub client with API key

    pass  

def get_first_stock_symbol(gemini_output):
    try:
        data = json.loads(gemini_output) # parse the gemini output as JSON
        first_stock = data["stocksAffected"][0]["ticker"] # get the ticker of the first stock in the list
        return first_stock
    except Exception as e:
        print(f"Error parsing Gemini output: {e}")
        return None

app = Flask(__name__) # create a Flask app instance, where to look for templates and static files

@app.route('/') # when someone visits homepage do the below function
def home():
    #return render_template('index.html') # render the index.html template 
    return "Welcome to.... What did Trump do?"  # temporary response for testing 

if __name__ == '__main__':
    #print(genai.list_models()) # print available models in gemini
    # testing the functions on terminal
    news_text = get_news_articles("Donald Trump tech") # fetch news articles related to Donald Trump and tech sector
    print("------------Fetched News Articles----------")
    print(news_text) # print fetched news articles 

    financial_analysis = gemini_analysis(news_text, "Technology") # analyze the news articles for the technology 
    print("------------Financial Analysis from Gemini----------")
    print(financial_analysis) # print the financial analysis generated by gemini

    app.run(debug=True) # run the app in debug mode for development