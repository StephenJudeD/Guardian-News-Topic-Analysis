Guardian News Topic Analysis
============================

A sophisticated topic analysis tool that extracts, processes, and visualizes news articles from The Guardian using advanced natural language processing techniques. The system employs BERTopic for dynamic topic modeling and provides interactive visualizations through a Dash web interface.

🌟 Features
-----------

-   **Real-time Article Fetching**: Automatically retrieves articles from The Guardian's API with customizable date ranges
-   **Advanced Topic Modeling**: Uses BERT embeddings and BERTopic for state-of-the-art topic analysis
-   **Interactive Visualizations**:
    -   Topic clusters and hierarchies
    -   Temporal topic evolution
    -   Document embeddings visualization
    -   Topic probability distributions
    -   Term importance rankings
-   **Flexible Date Filtering**: Analyze news trends across custom time periods
-   **Preprocessing Pipeline**: Robust text cleaning and preparation for analysis

🚀 Getting Started
------------------

### Prerequisites

bash

Copy

```
pip install -r requirements.txt

```

### Environment Variables

Create a `.env` file with:

env

Copy

```
GUARDIAN_API_KEY=your_guardian_api_key
EMBEDDING_MODEL=all-MiniLM-L6-v2

```

### Running the Application

bash

Copy

```
python main.py

```

Navigate to `http://localhost:8050` to access the dashboard.

💡 Use Cases
------------

1.  **News Trend Analysis**

    -   Track emerging topics over time
    -   Identify trending themes in specific news sections
    -   Monitor topic evolution and relationships
2.  **Media Research**

    -   Analyze media coverage patterns
    -   Study topic distribution across different sections
    -   Compare narrative changes over time
3.  **Content Strategy**

    -   Identify underreported topics
    -   Understand topic relationships
    -   Track seasonal content patterns

🔄 Adapting to Other Sources
----------------------------

The system can be modified to work with other news sources or RSS feeds by:

1.  Creating a new data fetcher class similar to `fetch_guardian_articles_enhanced`
2.  Implementing the appropriate API/RSS feed parser
3.  Mapping the source's data structure to the expected DataFrame format:

    python

    RunCopy

    ```
    {
        'title': str,
        'content': str,
        'section': str,
        'published': datetime,
        'wordcount': int,
        'url': str,
        'author': str
    }

    ```

### Example for RSS Integration:

python

RunCopy

```
import feedparser

def fetch_rss_feed(url, days_back=30):
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        articles.append({
            'title': entry.title,
            'content': entry.description,
            'published': entry.published,
            # Map other fields accordingly
        })

    return pd.DataFrame(articles)

```

📊 Visualization Examples
-------------------------

The dashboard provides multiple interactive visualizations:

-   Topic Clusters
-   Hierarchical Topic Relationships
-   Topic Evolution Over Time
-   Document Embeddings
-   Term Importance
-   Topic Distribution

🛠 Technical Architecture
-------------------------

-   **Frontend**: Dash/Plotly for interactive visualizations
-   **Backend**: Flask server with Python processing
-   **NLP Pipeline**:
    -   BERT embeddings for semantic understanding
    -   BERTopic for dynamic topic modeling
    -   UMAP for dimensionality reduction
    -   HDBSCAN for clustering

📝 Future Improvements
----------------------

-   [ ]  Add support for multiple news sources
-   [ ]  Implement real-time topic updating
-   [ ]  Add sentiment analysis
-   [ ]  Enable topic comparison across sources
-   [ ]  Add export functionality for analysis results
-   [ ]  Implement user-defined topic labeling

🤝 Contributing
---------------

Contributions are welcome! Please feel free to submit a Pull Request.

📄 License
----------

This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
------------------

-   The Guardian for their API
-   BERTopic developers
-   Sentence-Transformers team
