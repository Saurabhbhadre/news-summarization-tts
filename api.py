from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
from typing import Dict, List
from textblob import TextBlob
import spacy
from collections import Counter
import os
from gtts import gTTS
from deep_translator import GoogleTranslator
from pydantic import BaseModel

app = FastAPI()

# Load spaCy NLP model for topic extraction
nlp = spacy.load("en_core_web_sm")

# Replace with your NewsAPI key
NEWS_API_KEY = "73745642ac07452b97615cdfe6d653b0"

class TTSRequest(BaseModel):
    text: str

def fetch_news(company: str) -> List[Dict]:
    """
    Fetches news articles using NewsAPI.
    """
    api_url = f"https://newsapi.org/v2/everything?q={company}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(api_url)

    if response.status_code != 200:
        return []

    data = response.json()
    articles = data.get("articles", [])[:10]  # Get only 10 latest articles

    news_data = []
    for article in articles:
        try:
            title = article["title"]
            description = article["description"] or "No description available."
            content = article.get("content", description)
            url = article["url"]
            source = article["source"]["name"]
            published_at = article["publishedAt"]

            # Summarization (Extract first 2 sentences)
            summary = ". ".join(content.split(". ")[:2]) + "..."

            # Sentiment Analysis
            sentiment_score = TextBlob(content).sentiment.polarity
            sentiment = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"

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
    topic_counts = Counter()

    for article in articles:
        topic_counts.update(article["Topics"])

    return {
        "Sentiment Distribution": dict(sentiment_counts),
        "Most Mentioned Topics": topic_counts.most_common(3)
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

@app.post("/generate_tts")
def generate_tts(request: TTSRequest):
    """
    Generates a Hindi TTS audio file and returns a URL to access it.
    """
    text = request.text.strip()

    if not text:
        return {"error": "No text provided for TTS."}

    try:
        # Translate English summary to Hindi
        hindi_text = GoogleTranslator(source="auto", target="hi").translate(text)

        # Generate Hindi TTS
        tts = gTTS(hindi_text, lang="hi")
        file_path = "/tmp/tts_output.mp3"
        tts.save(file_path)

        return {"audio_url": "https://saurabhbhadre-news-summarization-api.hf.space/download_tts"}

    except Exception as e:
        return {"error": f"TTS generation failed: {str(e)}"}

@app.get("/download_tts")
def download_tts():
    """
    Serve the TTS audio file directly.
    """
    file_path = "/tmp/tts_output.mp3"
    
    if not os.path.exists(file_path):
        return {"error": "TTS file not found."}
    
    return FileResponse(file_path, media_type="audio/mpeg", filename="tts_output.mp3")
