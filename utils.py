import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from gtts import gTTS
import os
from collections import Counter

nltk.download("punkt")
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

def get_news_articles(company_name):
    """Fetch news articles related to the given company."""
    search_url = f"https://news.google.com/search?q={company_name}&hl=en&gl=US&ceid=US:en"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = []
    for item in soup.find_all("article")[:10]:  
        title_element = item.find("a")
        if title_element:
            title = title_element.text.strip()
            link = "https://news.google.com" + title_element["href"][1:]
            articles.append({"title": title, "url": link})
    
    return articles

def summarize_text(text, num_sentences=2):
    """Summarizes text by extracting key sentences."""
    sentences = sent_tokenize(text)
    return " ".join(sentences[:num_sentences])

def analyze_sentiment(text):
    """Performs sentiment analysis on text."""
    score = sia.polarity_scores(text)["compound"]
    return "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"

def comparative_analysis(articles):
    """Generates comparative sentiment analysis of articles."""
    sentiments = [article["sentiment"] for article in articles]
    sentiment_counts = Counter(sentiments)
    return {
        "Sentiment Distribution": dict(sentiment_counts),
        "Total Articles": len(articles)
    }

def generate_tts(text, filename="static/output.mp3"):
    """Generates Hindi text-to-speech audio."""
    tts = gTTS(text=text, lang="hi")
    os.makedirs("static", exist_ok=True)
    filepath = os.path.join("static", filename)
    tts.save(filepath)
    return filepath
