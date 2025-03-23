from fastapi import FastAPI
import requests
from typing import Dict, List
from textblob import TextBlob
import spacy
from collections import Counter

app = FastAPI()

# Load spaCy NLP model for topic extraction
nlp = spacy.load("en_core_web_sm")

# 🔹 Replace with your API key from https://newsapi.org/
NEWS_API_KEY = "73745642ac07452b97615cdfe6d653b0"

def fetch_news(company: str) -> List[Dict]:
    """
    Fetches news articles using NewsAPI.
    """
    api_url = f"https://newsapi.org/v2/everything?q={company}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    
    response = requests.get(api_url)
    print(f"🔍 Fetching news from: {api_url}")
    print(f"🔄 Response Code: {response.status_code}")

    if response.status_code != 200:
        return []

    data = response.json()
    articles = data.get("articles", [])[:10]  # Get only 10 latest articles

    news_data = []
    for article in articles:
        try:
            title = article["title"]
            description = article["description"] or "No description available."
            content = article.get("content", description)  # Use content if available
            url = article["url"]
            source = article["source"]["name"]
            published_at = article["publishedAt"]

            # Summarization (Extract first 2 sentences)
            summary = ". ".join(content.split(". ")[:2]) + "..."

            # Sentiment Analysis
            sentiment_score = TextBlob(content).sentiment.polarity
            if sentiment_score > 0:
                sentiment = "Positive"
            elif sentiment_score < 0:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            # Extract Topics using spaCy
            doc = nlp(content)
            topics = list(set([ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "TECH", "GPE"]]))

            news_data.append({
                "Title": title,
                "Summary": summary,
                "Sentiment": sentiment,
                "Topics": topics,
                "URL": url,
                "Source": source,
                "Published At": published_at
            })

        except Exception as e:
            print(f"⚠️ Error processing article: {e}")
            continue

    return news_data

def comparative_sentiment_analysis(articles: List[Dict]) -> Dict:
    """
    Performs comparative sentiment analysis on multiple articles.
    """
    sentiment_counts = Counter([article["Sentiment"] for article in articles])

    common_topics = set()
    topic_counts = Counter()

    for article in articles:
        common_topics.update(article["Topics"])
        topic_counts.update(article["Topics"])

    topic_overlap = {
        "Common Topics": list(common_topics),
        "Most Mentioned Topics": topic_counts.most_common(3)
    }

    return {
        "Sentiment Distribution": dict(sentiment_counts),
        "Topic Overlap": topic_overlap
    }

@app.get("/get_news")
def get_news(company: str):
    """
    API Endpoint to fetch news articles related to a company.
    """
    news_articles = fetch_news(company)

    if not news_articles:
        return {"error": "No news found for this company."}

    sentiment_analysis = comparative_sentiment_analysis(news_articles)

    return {
        "Company": company,
        "Articles": news_articles,
        "Comparative Sentiment Score": sentiment_analysis
    }
