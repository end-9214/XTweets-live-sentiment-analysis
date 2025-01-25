# XTweets Live Sentiment Analysis

Real-time Twitter sentiment analysis using CrewAI agents and Google Gemini.

**Repo**: [github.com/end-9214/XTweets-live-sentiment-analysis](https://github.com/end-9214/XTweets-live-sentiment-analysis)

## Features
- Scrapes 5 latest tweets from 5 users
- AI-powered sentiment analysis
- Interactive chat interface
- JSON data storage

## Quick Start

1. **Install**:
```bash
git clone https://github.com/end-9214/XTweets-live-sentiment-analysis.git
cd XTweets-live-sentiment-analysis
pip install google-generativeai crewai ntscraper
```

2. **Configure**:
- Get Gemini API key from [AI Studio](https://aistudio.google.com/)
- Replace `your-api-key-here` in `sentiment_analyzer.py`

3. **Run**:
```bash
python sentiment_analyzer.py
```

## Usage
- Default users analyzed: 
  `@elonmusk, @BarackObama, @BillGates, @nytimes, @CNN`
- Chat interface appears after analysis:
  ```bash
  Which user's sentiments? > elonmusk
  --- Latest sentiments for @elonmusk ---
  1. POSITIVE: Launching new SpaceX project...
  2. NEUTRAL: Reminder about shareholder meeting...
  ```

## Files
- `sentiment_analyzer.py`: Main script
- `tweets_data.json`: Raw tweet storage
- `sentiments.json`: Analysis results

## Requirements
- Python 3.11+
- Valid Gemini API key
