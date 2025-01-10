# topic_analyzer.py
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
import numpy as np
from app.config import Config
from app.utils import preprocess_text, fetch_guardian_articles_enhanced, filter_dataframe_by_date

class TopicAnalyzer:
    def __init__(self):
        self.config = Config()
        self.setup_nltk()
        self.sentence_transformer = SentenceTransformer(self.config.EMBEDDING_MODEL)
        self.df = None
        self.topic_model = None
        self.embeddings = None

    def setup_nltk(self):
        nltk.download('stopwords')
        nltk.download('punkt')

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

        umap_model = UMAP(
            n_neighbors=15,
            n_components=5,
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

    def load_initial_data(self):
        """Load initial month of data"""
        self.df = fetch_guardian_articles_enhanced(
            api_key=self.config.GUARDIAN_API_KEY,
            days_back=self.config.DEFAULT_DAYS
        )
        return self.df is not None

    def generate_embeddings(self, docs):
        """Generate embeddings with batch processing"""
        embeddings = []
        for i in range(0, len(docs), self.config.BATCH_SIZE):
            batch = docs[i:i + self.config.BATCH_SIZE]
            batch_embeddings = self.sentence_transformer.encode(
                batch,
                show_progress_bar=True
            )
            embeddings.extend(batch_embeddings)
        return np.array(embeddings)

    def visualize_documents_with_embeddings(self, docs, topic_model):
        """Visualize documents within topics"""
        if self.embeddings is None:
            self.embeddings = self.generate_embeddings(docs)

        reduced_embeddings = UMAP(
            n_neighbors=10,
            n_components=2,
            min_dist=0.0,
            metric='cosine'
        ).fit_transform(self.embeddings)

        return topic_model.visualize_documents(
            docs,
            reduced_embeddings=reduced_embeddings,
            hide_document_hover=False
        )

    def visualize_document_probabilities(self, docs, topic_model):
        """Generate and visualize topic-document probabilities"""
        topics, probs = topic_model.fit_transform(docs)
        return topic_model.visualize_distribution(probs[0])

    def analyze_topics(self, df, n_topics=10):
        """Main topic analysis function"""
        vectorizer_model, umap_model, hdbscan_model = self.setup_models()
        
        self.topic_model = BERTopic(
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
        
        # Generate embeddings if not already done
        if self.embeddings is None:
            self.embeddings = self.generate_embeddings(processed_docs)

        # Fit the model
        topics, probs = self.topic_model.fit_transform(
            processed_docs,
            self.embeddings
        )

        # Generate temporal analysis
        timestamps = df['published_date'].tolist()
        topics_over_time = self.topic_model.topics_over_time(
            docs=processed_docs,
            topics=topics,
            timestamps=timestamps,
            global_tuning=True,
            evolution_tuning=True,
            nr_bins=10
        )

        # Generate all visualizations
        visualizations = {
            'topic_viz': self.topic_model.visualize_topics(),
            'hierarchy_viz': self.topic_model.visualize_hierarchy(),
            'time_viz': self.topic_model.visualize_topics_over_time(topics_over_time),
            'doc_viz': self.visualize_documents_with_embeddings(processed_docs, self.topic_model),
            'barchart_viz': self.topic_model.visualize_barchart(),
            'terms_viz': self.topic_model.visualize_term_rank(),
            'prob_viz': self.visualize_document_probabilities(processed_docs, self.topic_model)
        }

        return {
            'model': self.topic_model,
            'topics': topics,
            'probs': probs,
            'topics_over_time': topics_over_time,
            'visualizations': visualizations,
            'processed_docs': processed_docs
        }

    def run_analysis(self, start_date=None, end_date=None):
        """Run analysis with optional date filtering"""
        if self.df is None:
            if not self.load_initial_data():
                raise ValueError("Failed to load initial data")

        # Filter data if dates provided
        working_df = filter_dataframe_by_date(self.df, start_date, end_date) if start_date and end_date else self.df

        if working_df.empty:
            raise ValueError("No articles in specified date range")

        return self.analyze_topics(working_df)
