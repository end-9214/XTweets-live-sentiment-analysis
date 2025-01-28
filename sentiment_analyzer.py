import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import json
from google.generativeai import configure
import tweepy

load_dotenv()
configure(api_key=os.getenv('GEMINI_API_KEY'))

llm = LLM(model="gemini/gemini-pro")

@tool("Twitter Scraper Tool")
def twitter_scraper(usernames: list) -> str:
    """Scrapes recent 5 tweets from specified Twitter handles using tweepy.
       Returns success or error message.
    """
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        return "Error: Twitter API keys are missing. Set environment variables."

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    tweets_data = {}
    for username in usernames:
        try:
            user = api.get_user(screen_name=username)
            tweets = api.user_timeline(user_id=user.id, count=5, tweet_mode="extended")
            tweets_list = []
            for tweet in tweets:
                tweet_data = {
                    "id": str(tweet.id),
                    "date": tweet.created_at.isoformat(),
                    "content": tweet.full_text,
                    "url": f"https://twitter.com/{username}/status/{tweet.id}",
                    "retweet_count": tweet.retweet_count,
                    "favorite_count": tweet.favorite_count
                }
                tweets_list.append(tweet_data)
            tweets_data[username] = tweets_list
        except tweepy.TweepyException as e:  
            return f"Error scraping @{username}: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    with open('tweets.json', 'w', encoding='utf-8') as f:
        json.dump(tweets_data, f, indent=4, ensure_ascii=False)

    return "Tweets scraped and saved successfully"

@tool("Sentiment Analysis Tool")
def sentiment_analyzer(input_file: str) -> str:
    """Analyzes tweet sentiments using Gemini AI.
       Reads tweet data from a JSON file, performs sentiment analysis,
       and saves the results (including original tweet data and sentiment)
       to a new JSON file. Returns success message.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            tweets_data = json.load(f)
    except FileNotFoundError:
        return f"Error: Input file '{input_file}' not found. Make sure the Twitter scraper tool has run."
    except json.JSONDecodeError:
        return f"Error: Invalid JSON format in '{input_file}'. Check the output of the Twitter scraper."
    except Exception as e:
        return f"An unexpected error occurred while reading the file: {e}"

    results = {}
    for username, tweets in tweets_data.items():
        user_results = []
        for tweet in tweets:
            response = llm.generate_content(
                f"Analyze sentiment of this tweet. Respond ONLY with: positive, negative, or neutral. Tweet: {tweet['content']}"
            )
            sentiment = response.strip().lower()
            tweet['sentiment'] = sentiment
            user_results.append(tweet)
        results[username] = user_results

    with open('sentiments.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    return "Sentiment analysis completed and saved"

twitter_agent = Agent(
    role='Social Media Scraper',
    goal='Collect recent tweets',
    backstory='Expert in data collection',
    tools=[twitter_scraper],
    llm=llm,
    verbose=True
)

analysis_agent = Agent(
    role='Sentiment Analyst',
    goal='Analyze sentiment',
    backstory='NLP specialist',
    tools=[sentiment_analyzer],
    llm=llm,
    verbose=True
)

scrape_task = Task(
    description='Gather last 5 tweets from elonmusk, BillGates, sundarpichai',
    agent=twitter_agent,
    expected_output='JSON file containing recent tweets (tweets.json)'
)

analyze_task = Task(
    description='Perform sentiment analysis',
    agent=analysis_agent,
    expected_output='JSON file with sentiment scores (sentiments.json)',
    context=[scrape_task]
)

social_media_crew = Crew(
    agents=[twitter_agent, analysis_agent],
    tasks=[scrape_task, analyze_task],
    verbose=True
)

result = social_media_crew.kickoff()

print(f"Workflow completed. Result: {result}")