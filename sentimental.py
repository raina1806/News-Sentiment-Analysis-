import nltk
import requests
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
from textblob import TextBlob
from newspaper import Article
import streamlit as st

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Function to fetch news articles from the API
def fetch_news(api_key, query="latest"):
    url = f"https://newsapi.org/v2/everything?q=bitcoin&apiKey=b64c1e5c018044ff96a89c10e0376f91"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        st.error(f"Error fetching news: {response.status_code}")
        return []

# Function to summarize text using word frequencies
def summarize_text(text, max_sentences=2):
    if not text:  # Handle empty or None text
        return "No summary available."
    
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())
    
    # Calculate word frequencies
    word_frequencies = Counter(word for word in words if word.isalnum() and word not in stop_words)
    max_frequency = max(word_frequencies.values(), default=1)
    
    # Normalize frequencies
    word_frequencies = {word: freq / max_frequency for word, freq in word_frequencies.items()}
    
    # Score sentences
    sentences = sent_tokenize(text)
    sentence_scores = {sent: sum(word_frequencies.get(word.lower(), 0) for word in word_tokenize(sent)) for sent in sentences}
    
    # Select top sentences
    summarized = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    return " ".join(summarized)

# Categorize articles based on keywords
categories = {
    "technology": ["tech", "AI", "blockchain", "software"],
    "sports": ["football", "cricket", "tennis", "NBA"],
    "finance": ["stocks", "economy", "crypto", "business"],
}

def categorize_article(title):
    for category, keywords in categories.items():
        if any(keyword.lower() in title.lower() for keyword in keywords):
            return category
    return "general"

# Sentiment Analysis Function
def analyze_sentiment(text):
    if not text:  # Handle empty or None text
        return "Neutral", 0
    
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    # Determine sentiment label
    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    
    return sentiment, polarity

# Streamlit UI
st.set_page_config(page_title="AI-Powered News Aggregator with Sentiment Analysis", layout="wide")
st.title("📰 AI-Powered News Aggregator with Sentiment Analysis")

# API Key input
api_key = st.text_input("🔑 Enter the API Key:", type="password")

# Add sidebar for branding and filters
with st.sidebar:
    st.header("Customize Your Feed")
    query = st.text_input("🔍 Search News:", "AI")
    max_sentences = st.slider("Summary Length (Sentences):", 1, 5, 2)
    sentiment_filter = st.selectbox("Filter by Sentiment:", ["All", "Positive", "Neutral", "Negative"])
    st.markdown("## About This App")
    st.write("This app fetches the latest news, summarizes it, and provides sentiment analysis. Categories include Technology, Sports, Finance, and more!")

# Proceed if API key is provided
if api_key:
    # Fetch articles from the news API
    articles = fetch_news(api_key, query=query)
    
    if articles:
        st.subheader(f"Latest News for **{query}**")
        
        for article in articles:
            title = article['title']
            description = article.get('description', '')
            url = article['url']
            category = categorize_article(title)
            summary = summarize_text(description, max_sentences)

            # Sentiment analysis for the summary or description
            sentiment, polarity = analyze_sentiment(description)

            # Apply sentiment filter
            if sentiment_filter != "All" and sentiment != sentiment_filter:
                continue

            with st.container():
                col1, col2 = st.columns([1, 4])

                # Show category and image on the left
                with col1:
                    st.markdown(f"**Category:** `{category}`")
                    if article.get('urlToImage'):
                        st.image(article['urlToImage'], use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/150", caption="No Image Available")
                
                # Show article details on the right
                with col2:
                    st.markdown(f"### [{title}]({url})")
                    st.write(f"**Summary:** {summary}")
                    st.write(f"**Sentiment:** {sentiment} (Polarity: {polarity:.2f})")
                
                # Add a horizontal divider
                st.write("---")
    else:
        st.warning("No articles found for your query.")
else:
    st.info("Please enter a valid API key to proceed.")
