from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
from app.config import Config
import numpy as np

class TopicAnalyzer:
    def __init__(self):
        self.config = Config()
        self.setup_nltk()
        self.setup_transformer()

    def setup_nltk(self):
        nltk.download('stopwords')
        nltk.download('punkt')

    def setup_transformer(self):
        if self.config.USE_LIGHTWEIGHT:
            # Lighter alternative
            self.sentence_transformer = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        else:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')

    def setup_models(self):
        stop_words = set(stopwords.words('english'))
        custom_stop_words = {
            'said', 'says', 'would', 'could', 'guardian', 'according',
            'also', 'like', 'one', 'two', 'three', 'year', 'years',
            'today', 'yesterday', 'week', 'month', 'first', 'last', 'time', 'th'
        }
        stop_words.update(custom_stop_words)

        vectorizer_model = CountVectorizer(
            stop_words=list(stop_words),
            min_df=2,
            max_df=0.95,
            ngram_range=(1, 3)
        )

        # Lighter UMAP settings for Heroku
        umap_model = UMAP(
            n_neighbors=10,  # Reduced from 15
            n_components=3,  # Reduced from 5
            min_dist=0.0,
            metric='cosine',
            random_state=42
        )

        hdbscan_model = HDBSCAN(
            min_cluster_size=5,
            metric='euclidean',
            cluster_selection_method='eom',
            prediction_data=True
        )

        return vectorizer_model, umap_model, hdbscan_model

    def analyze_topics(self, df, n_topics=10):
        vectorizer_model, umap_model, hdbscan_model = self.setup_models()
        
        topic_model = BERTopic(
            language="english",
            calculate_probabilities=True,
            verbose=True,
            min_topic_size=3,
            nr_topics=n_topics,
            vectorizer_model=vectorizer_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            embedding_model=self.sentence_transformer
        )

        processed_docs = [preprocess_text(doc) for doc in df['content'].tolist()]

        # Batch processing for memory efficiency
        batch_size = 32
        embeddings = []
        for i in range(0, len(processed_docs), batch_size):
            batch = processed_docs[i:i + batch_size]
            batch_embeddings = self.sentence_transformer.encode(batch, show_progress_bar=True)
            embeddings.extend(batch_embeddings)
        
        embeddings = np.array(embeddings)

        topics, probs = topic_model.fit_transform(processed_docs, embeddings)

        timestamps = df['published_date'].tolist()
        topics_over_time = topic_model.topics_over_time(
            docs=processed_docs,
            topics=topics,
            timestamps=timestamps,
            global_tuning=True,
            evolution_tuning=True,
            nr_bins=10
        )

        return topic_model, topics, probs, topics_over_time

    # ... (rest of the methods remain the same)
