import requests
import pandas as pd
from datetime import datetime, timedelta
import nltk
import re
from tqdm import tqdm
import time

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    return text

def fetch_guardian_articles_enhanced(api_key, days_back=7):
    base_url = "https://content.guardianapis.com/search"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    params = {
        'api-key': api_key,
        'show-fields': 'bodyText,headline,byline,wordcount,shortUrl,thumbnail,lastModified',
        'page-size': 50,
        'order-by': 'newest',
        'from-date': start_date.strftime('%Y-%m-%d'),
        'to-date': end_date.strftime('%Y-%m-%d')
    }

    articles = []

    try:
        response = requests.get(base_url, params={**params, 'page': 1})
        if response.status_code == 200:
            data = response.json()
            total_pages = min(data['response']['pages'], 105)

            for page in tqdm(range(1, total_pages + 1), desc="Fetching articles"):
                response = requests.get(base_url, params={**params, 'page': page})
                if response.status_code == 200:
                    results = response.json()['response']['results']
                    
                    for article in results:
                        if 'fields' in article:
                            try:
                                wordcount = int(article['fields'].get('wordcount', 0))
                            except (ValueError, TypeError):
                                wordcount = 0

                            articles.append({
                                'title': article['webTitle'],
                                'content': article['fields'].get('bodyText', ''),
                                'section': article['sectionName'],
                                'published': article['webPublicationDate'],
                                'wordcount': wordcount,
                                'url': article['fields'].get('shortUrl', ''),
                                'author': article['fields'].get('byline', '')
                            })

                time.sleep(0.5)

    except Exception as e:
        print(f"Error fetching articles: {str(e)}")

    df = pd.DataFrame(articles)
    if not df.empty:
        df['content_length'] = df['content'].astype(str).str.len()
        df = df[df['content_length'] > 200]
        df['published_date'] = pd.to_datetime(df['published'])

    return df