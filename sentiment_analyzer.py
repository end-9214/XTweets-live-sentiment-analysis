import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import json
from google.generativeai import configure
from ntscraper import Nitter
import datetime

# Load environment variables
load_dotenv()
configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize LLM
llm = LLM(model="gemini/gemini-pro")

@tool("Tweet Scraper Tool")
def tweet_scraper(usernames: list) -> str:
    """Scrapes recent tweets from specified handles using Nitter.
       Returns success or error message.
    """
    scraper = Nitter()
    tweets_data = {}
    errors = []
    
    for username in usernames:
        try:
            # Get tweets using ntscraper
            tweets = scraper.get_tweets(username, mode='user', number=5)
            
            if not tweets['tweets']:
                tweets_data[username] = []
                continue
                
            tweets_list = []
            for tweet in tweets['tweets']:
                # Convert tweet timestamp to ISO format
                tweet_date = datetime.datetime.strptime(
                    tweet['date'], 
                    '%b %d, %Y · %I:%M %p UTC'
                ).isoformat()
                
                tweet_data = {
                    "id": tweet['link'].split('/')[-1],
                    "date": tweet_date,
                    "content": tweet['text'],
                    "url": tweet['link'],
                    "retweet_count": tweet.get('retweets', 0),
                    "favorite_count": tweet.get('likes', 0)
                }
                tweets_list.append(tweet_data)
            tweets_data[username] = tweets_list
            
        except Exception as e:
            errors.append(f"Error scraping @{username}: {str(e)}")

    # Save tweets to a JSON file
    output_file = 'tweets.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tweets_data, f, indent=4, ensure_ascii=False)

    if not any(tweets_data.values()):
        return "Error: No tweets were retrieved. Check usernames and try again."
        
    if errors:
        return f"Partial success. Tweets saved to {output_file}. Errors: {', '.join(errors)}"
    return f"Success: Tweets saved to {output_file}"

@tool("Sentiment Analysis Tool")
def sentiment_analyzer(input_file: str) -> str:
    """Analyzes tweet sentiments using Gemini AI."""
    try:
        # Read tweets file
        with open(input_file, 'r', encoding='utf-8') as f:
            tweets_data = json.load(f)
            
        if not tweets_data:
            return "Error: No tweet data found in the input file."

        results = {}
        valid_sentiments = {"positive", "negative", "neutral"}
        
        for username, tweets in tweets_data.items():
            if not tweets:  # Skip empty tweet lists
                continue
                
            user_results = []
            for tweet in tweets:
                try:
                    prompt = (
                        "Analyze the sentiment of this tweet. "
                        "Respond ONLY with one word: positive, negative, or neutral.\n\n"
                        f"Tweet: {tweet['content']}"
                    )
                    
                    response = llm.generate_content(prompt)
                    sentiment = response.strip().lower()
                    
                    if sentiment not in valid_sentiments:
                        print(f"Warning: Invalid sentiment '{sentiment}' for tweet {tweet['id']}")
                        sentiment = "neutral"
                        
                    tweet_result = tweet.copy()
                    tweet_result['sentiment'] = sentiment
                    user_results.append(tweet_result)
                    
                except Exception as e:
                    print(f"Error analyzing tweet {tweet['id']}: {str(e)}")
                    tweet_result = tweet.copy()
                    tweet_result['sentiment'] = "neutral"
                    tweet_result['error'] = str(e)
                    user_results.append(tweet_result)
                    
            results[username] = user_results

        # Save results
        output_file = 'sentiments.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        return f"Success: Sentiment analysis saved to {output_file}"
        
    except FileNotFoundError:
        return f"Error: Input file '{input_file}' not found"
    except json.JSONDecodeError:
        return f"Error: Invalid JSON format in '{input_file}'"
    except Exception as e:
        return f"Error: {str(e)}"

# Define Agents
twitter_agent = Agent(
    role='Social Media Scraper',
    goal='Collect recent tweets',
    backstory='Expert in data collection',
    tools=[tweet_scraper],
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

# Define Tasks
scrape_task = Task(
    description="Gather last 5 tweets from elonmusk, BillGates, and sundarpichai",
    expected_output="JSON file containing scraped tweets (tweets.json)",
    agent=twitter_agent
)

analyze_task = Task(
    description='Analyze sentiments in tweets.json',
    expected_output="JSON file containing sentiment analysis results (sentiments.json)",
    agent=analysis_agent,
    context=[scrape_task]
)

# Define Crew
social_media_crew = Crew(
    agents=[twitter_agent, analysis_agent],
    tasks=[scrape_task, analyze_task],
    verbose=True
)

if __name__ == "__main__":
    try:
        result = social_media_crew.kickoff()
        print(f"Workflow completed. Result: {result}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error during execution: {str(e)}")