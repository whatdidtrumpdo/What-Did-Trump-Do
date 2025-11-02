# main Flask app file

from flask import Flask, request, jsonify, render_template # import Flask which is the web framework
from flask_cors import CORS
from dotenv import load_dotenv # import load_dotenv to load environment variables
import os # import os to access environment variables
import requests # import requests to make HTTP requests to NewsAPI
#import finhub # import finhub-python package to access Finhub API
import pandas as pd # import pandas for data manipulation
import time
import mplfinance as mpf # import mplfinance for financial charting
import google.generativeai as genai
import json

load_dotenv() # load api keys from .env file for security

genai.configure(api_key=os.getenv("GENAI_API_KEY")) # what this does it set the API key for gemini so that we can make requests to the API
model = genai.GenerativeModel('gemini-2.5-flash') # specify the model version to use


def get_gemini_analysis(news_articles, sector): # takes in news articles and sector as input, might change to take only 1 article later
    prompt = f"""
        Analyze the following news articles about Donal Trump's recent actions and their impact on the
        {sector} sector: Based on this, provide:

        1. Investor Sentiment (Bullish, Bearish, or Neutral) and explain why
        2. Short-Term Market Outlook (Up, Down, Consolidate) and explain why
        3. Long-Term Market Outlook (Up, Down, Consolidate) and explain why
        4. 4 popular example stocks in this sector that are most likely to be affected, along with their predicted short-term movement (e.g., AAPL: Up, GOOG: Consolidate).
        5. A concise, paragraph-long summary suitable for a financial news report and retail investor.

    Format your response strictly as JSON and do not include anything else but the JSON object. Be sure to use the following structure
    and Do not include any surrounding characters, backticks (```), or formatting outside of the JSON object itself:
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
        print("=== SENDING PROMPT TO GEMINI ===")
        
        response = model.generate_content(prompt)
        gemini_raw_text = response.text # get the raw text response from gemini
        
        print("=== RAW GEMINI RESPONSE ===")
        print(gemini_raw_text)
        print("=== END RAW RESPONSE ===")

        # Clean the response - remove markdown code blocks
        cleaned_text = gemini_raw_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:] # remove the starting ```json, could prompt to not include it
        # if cleaned_text.startswith('```'):  # tried to prompt to exclude, but still did it
        #     cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip() # strip white space again after '''json removal

        print("=== CLEANED RESPONSE ===")
        print(cleaned_text)

        if not cleaned_text.startswith('{'): # basic check to see if response is JSON
            print("ERROR: Response doesn't start with '{'")
            # Return a fallback response for the hackathon
            return create_fallback_response(sector)

        convert = json.loads(cleaned_text) # converts JSON to python dictionary, with key being the field names and values being gemini responses
        print("=== SUCCESSFULLY CONVERTED JSON TO PYTHON DICTIONARY ===")
        return convert
        
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Problematic text: {cleaned_text[:500]}...")
        return create_fallback_response(sector)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return create_fallback_response(sector) 

def create_fallback_response(sector): # if gemini fails, return this hardcoded response
    """Fallback response when Gemini fails"""
    return {
        "sentiment": "gemini-2.5-pro",
        "whySentiment": "Mixed market signals from recent news coverage.",
        "shortTermOutlook": "Consolidate", 
        "whyShortTermOutlook": "Market digesting recent political developments.",
        "longTermOutlook": "Up",
        "whyLongTermOutlook": "Technology sector fundamentals remain strong despite political volatility.",
        "stocksAffected": [
            {"ticker": "AAPL", "movement": "Up"},
            {"ticker": "MSFT", "movement": "Up"},
            {"ticker": "GOOGL", "movement": "Consolidate"},
            {"ticker": "TSLA", "movement": "Down"}
        ],
        "newsSummary": "Recent developments show mixed impact on technology sector. Investors are advised to monitor policy changes that may affect tech regulation and trade policies. Key stocks to watch include AAPL, MSFT, GOOGL, and TSLA as they navigate the current political landscape."
    }

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




# def Finhub_charts(): # placeholder for Finhub charts function
#     finhub_client = finhub.Client(api_key=os.getenv("FINHUB_API_KEY")) # initialize Finhub client with API key

#     pass  

# def get_first_stock_symbol(gemini_output):
#     try:
#         data = json.loads(gemini_output) # parse the gemini output as JSON
#         first_stock = data["stocksAffected"][0]["ticker"] # get the ticker of the first stock in the list
#         return first_stock
#     except Exception as e:
#         print(f"Error parsing Gemini output: {e}")
#         return None

app = Flask(__name__, static_folder='static', template_folder='templates') # create a Flask app instance, where to look for templates and static files
CORS(app)

@app.route('/')  # displays home page at root URL ('index.html')
def home():
    return render_template('index.html')  # serve the index.html file from the static folder

@app.route('/analyze', methods=['POST'])
def analyze_sector():
    try:
        # HARDCODE technology sector for the hackathon
        sector = "technology"
        
        news_query = f"Donald Trump AND {sector}"
        news_articles_text = get_news_articles(news_query)

        if not news_articles_text: 
            return jsonify({"error": "Could not retrieve news articles for this sector."}), 500

        # Call get_gemini_analysis ONCE, and it returns a Python dictionary
        analysis_data = get_gemini_analysis(news_articles_text, sector)

        # Return the analysis data
        response_payload = {
            # get the values from each key in the analysis_data dictionary, default to none' or empty list if key not found
            # usuall using .get() method to avoid KeyError common with direct indexing '[]'
            "sector": sector,
            "sentiment": analysis_data.get('sentiment'), 
            "whySentiment": analysis_data.get('whySentiment'),
            "shortTermOutlook": analysis_data.get('shortTermOutlook'),
            "whyShortTermOutlook": analysis_data.get('whyShortTermOutlook'),
            "longTermOutlook": analysis_data.get('longTermOutlook'),
            "whyLongTermOutlook": analysis_data.get('whyLongTermOutlook'),
            "stocksAffected": analysis_data.get('stocksAffected'),
            "newsSummary": analysis_data.get('newsSummary')
        }
        # converts into json file  and returns with 200 OK status
        # json file is easy to parse on frontend with JavaScript. Backend and frontend communicate using JSON
        return jsonify(response_payload), 200 
        
    except Exception as e:
        print(f"Server error in /analyze: {e}")
        return jsonify({"error": str(e)}), 500

# def home():
#     #return render_template('index.html') # render the index.html template 
#     return "Welcome to.... What did Trump do?"  # temporary response for testing 



if __name__ == '__main__':
    #print(genai.list_models()) # print available models in gemini
    # testing the functions on terminal

    """
        news_text = get_news_articles("Donald Trump tech") # fetch news articles related to Donald Trump and tech sector
    print("------------Fetched News Articles----------")
    print(news_text) # print fetched news articles 

    financial_analysis = gemini_analysis(news_text, "Technology") # analyze the news articles for the technology 
    print("------------Financial Analysis from Gemini----------")
    print(financial_analysis) # print the financial analysis generated by gemini

    """
    print(" AI Flask App...")
    if not os.getenv("GEMINI_API_KEY"): print("WARNING: GEMINI_API_KEY not loaded!")
    if not os.getenv("NEWS_API_KEY"): print("WARNING: NEWS_API_KEY not loaded!")
    if not os.getenv("ELEVENLABS_API_KEY"): print("WARNING: ELEVENLABS_API_KEY not loaded!")
    app.run(debug=True, port=5000) # run the app in debug mode for development on port 5000
