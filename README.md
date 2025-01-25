# XTweets Live Sentiment Analysis 🔍

[![GitHub stars](https://img.shields.io/github/stars/end-9214/XTweets-live-sentiment-analysis)](https://github.com/end-9214/XTweets-live-sentiment-analysis/stargazers)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

Real-time Twitter sentiment analysis system using CrewAI agents powered by Google Gemini. Analyzes latest tweets from popular accounts and provides interactive insights.

GitHub Repository: [https://github.com/end-9214/XTweets-live-sentiment-analysis](https://github.com/end-9214/XTweets-live-sentiment-analysis)

## 🌟 Features

- Live Twitter data scraping for 5 popular accounts
- AI-powered sentiment classification (Positive/Neutral/Negative)
- Interactive terminal interface
- JSON data persistence
- Rate-limited API handling

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Google Gemini API key

### Installation
```bash
# Clone repository
git clone https://github.com/end-9214/XTweets-live-sentiment-analysis.git
cd XTweets-live-sentiment-analysis

# Install dependencies
pip install google-generativeai crewai ntscraper

# Configure API key (edit sentiment_analyzer.py)
nano sentiment_analyzer.py
# Replace "your-api-key-here" with your Gemini API key
```

## 🤖 CrewAI Agent Architecture

### Agent Workflow

```bash
    sequenceDiagram
    participant User
    participant DataCollector
    participant SentimentAnalyzer
    participant Gemini
    
    User->>DataCollector: Trigger analysis
    DataCollector->>Twitter: Scrape tweets
    Twitter-->>DataCollector: Raw tweets
    DataCollector->>SentimentAnalyzer: Pass data
    SentimentAnalyzer->>Gemini: API request
    Gemini-->>SentimentAnalyzer: Sentiment labels
    SentimentAnalyzer->>User: Display results
    ```

## X Data Collector Agent
### Key Configuration:
```python
    Agent(
    name="X Data Collector",
    role="Twitter data scraping specialist",
    goal="Collect latest 5 tweets from 5 target accounts",
    backstory="Expert in social media data harvesting",
    llm=gemini_llm,
    verbose=True
)
```
