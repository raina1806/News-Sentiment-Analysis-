from flask import Flask, render_template, request
import requests
import config  # Ensure your API key is in this file
from textblob import TextBlob


app = Flask(__name__)

# Function to fetch news articles from the API
def fetch_news(query="latest", category=""):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={config.API_KEY}"
    if category:
        url += f"&category={category}"
    
    print(f"Fetching news with URL: {url}")  # Log the URL for debugging
    
    response = requests.get(url)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('articles', [])
    else:
        print("Error fetching news:", response.status_code)
        return []

# Categorize articles based on keywords
categories = {
    "Technology": ["tech", "AI", "blockchain", "software"],
    "Sports": ["football", "cricket", "tennis", "NBA"],
    "Finance": ["stocks", "economy", "crypto", "business"],
}

def categorize_article(title):
    for category, keywords in categories.items():
        if any(keyword.lower() in title.lower() for keyword in keywords):
            return category
    return "General"

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

@app.route('/', methods=['GET', 'POST'])
def index():
    query = "latest"  # Default query
    category = ""  # Default category (empty means no category filter)
    sentiment_filter = "All"  # Default sentiment filter
    
    # Get search query and filters from user input
    if request.method == 'POST':
        query = request.form.get('search_query', "latest")
        category = request.form.get('category_filter', "")
        sentiment_filter = request.form.get('sentiment_filter', "All")
    
    # Fetch articles based on the query and category
    articles = fetch_news(query=query, category=category)

    # Categorize and analyze sentiment of each article
    categorized_articles = []
    for article in articles:
        title = article.get('title')
        description = article.get('description', '')
        url = article.get('url')
        image = article.get('urlToImage', 'https://via.placeholder.com/150')  # Default placeholder image
        
        # Categorize the article
        category = categorize_article(title)
        
        # Sentiment analysis
        sentiment, polarity = analyze_sentiment(description)

        # Apply sentiment filter
        if sentiment_filter != "All" and sentiment != sentiment_filter:
            continue
        
        # Prepare the article data for rendering
        categorized_articles.append({
            'title': title,
            'url': url,
            'category': category,
            'description': description,
            'sentiment': sentiment,
            'polarity': polarity,
            'image': image
        })

    return render_template('index.html', articles=categorized_articles, 
                           categories=categories.keys(), sentiment_filter=sentiment_filter)

if __name__ == '__main__':
    app.run(debug=True)
