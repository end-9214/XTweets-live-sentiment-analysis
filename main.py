from crewai import Agent
import google.generativeai as genai
from ntscraper import Nitter
import json
import time
import os
from dotenv import load_env


os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '0'
os.environ["GEMINI_API_KEY"] = os.getenv('API_KEY')
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
gemini_llm = genai.GenerativeModel('gemini-pro')

x_data_collector = Agent(
    name="X Data Collector",
    role="Scrape 5 recent tweets from 5 users",
    goal="Collect latest tweets for analysis",
    backstory="Expert in social media data collection",
    llm=gemini_llm,
    verbose=True
)

sentiment_analyzer = Agent(
    name="Sentiment Analyzer",
    role="Analyze tweet sentiments",
    goal="Generate quick sentiment reports",
    backstory="NLP and sentiment analysis expert",
    llm=gemini_llm,
    verbose=True
)

def collect_tweets(users, num_tweets=5):
    scraper = Nitter(instance="https://nitter.net")
    tweets_data = {}
    
    for user in users:
        try:
            tweets = scraper.get_tweets(user, mode="user", number=num_tweets)
            if tweets and tweets.get("tweets"):
                tweets_data[user] = [{
                    "text": tweet["text"],
                    "created_at": tweet["date"]
                } for tweet in tweets["tweets"][:num_tweets]]
            else:
                print(f"No tweets found for {user}")
                tweets_data[user] = []
        except Exception as e:
            print(f"Error scraping {user}: {str(e)[:100]}...")
            tweets_data[user] = []
    
    return tweets_data

def analyze_sentiment(tweets_data):
    model = genai.GenerativeModel('gemini-pro')
    sentiment_results = {}
    
    for user, tweets in tweets_data.items():
        sentiments = []
        for tweet in tweets:
            try:
                time.sleep(1.5)
                response = model.generate_content(
                    f"Classify sentiment in one word (positive/neutral/negative) for: {tweet['text']}"
                )
                sentiment = response.text.strip().lower()
                sentiments.append({"text": tweet["text"], "sentiment": sentiment})
            except Exception as e:
                print(f"Analysis error: {str(e)[:100]}...")
                sentiments.append({"text": tweet["text"], "sentiment": "error"})
        sentiment_results[user] = sentiments
    
    return sentiment_results

def chat_about_sentiments(sentiment_results):
    print("\nChat about Tweet Sentiments (type 'exit' to quit)")
    while True:
        try:
            query = input("\nWhich user's sentiments? > ").strip().lower()
            if query == "exit":
                break
                
            matches = [user for user in sentiment_results if query in user.lower()]
            
            if not matches:
                print(f"User not found. Available: {list(sentiment_results.keys())}")
                continue
                
            for user in matches:
                print(f"\n--- Latest sentiments for @{user} ---")
                for idx, sentiment in enumerate(sentiment_results[user], 1):
                    print(f"{idx}. {sentiment['sentiment'].upper()}: {sentiment['text'][:60]}...")
                    
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break

def main():
    users = ["elonmusk", "BarackObama", "BillGates", "nytimes", "CNN"] 
    
    print("Collecting 5 recent tweets from 5 users...")
    tweets_data = collect_tweets(users)
    
    print("\nAnalyzing sentiments...")
    sentiment_results = analyze_sentiment(tweets_data)
    
    with open("tweets_data.json", "w") as f:
        json.dump(tweets_data, f, indent=2)
    with open("sentiments.json", "w") as f:
        json.dump(sentiment_results, f, indent=2)
    
    chat_about_sentiments(sentiment_results)

if __name__ == "__main__":
    main()