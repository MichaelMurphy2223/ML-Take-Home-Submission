from sentence_transformers import SentenceTransformer, util
from sklearn.preprocessing import normalize
import faiss
import pandas as pd
import numpy as np

class SpeakerRecommender:
    def __init__(self, speakers_csv, categories, topic):
        # Initialize with CSV path, categories, and topic
        self.speakers_csv = speakers_csv
        self.categories = categories
        self.topic = topic
        # Load the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Load speaker data
        self.df = pd.read_csv(self.speakers_csv)
        # Encode category and topic embeddings
        self.category_embeddings = self.model.encode(self.categories, convert_to_tensor=True)
        self.topic_embedding = self.model.encode(self.topic, convert_to_tensor=True)
        # Compute similarity scores between topic and categories
        self.similarity_scores = util.pytorch_cos_sim(self.topic_embedding, self.category_embeddings)[0]
        # Get top 5 most similar categories for the topic
        self.top_categories = [self.categories[i] for i in self.similarity_scores.argsort(descending=True)[:5]]
        print("Top categories for the topic:", self.top_categories)

    def weighted_encoding(self, row):
        # Create a weighted one-hot encoding for a list of categories
        cat_indices = [self.categories.index(i) for i in row]
        encoding = np.zeros(len(self.categories), dtype=np.float32)
        for i, j in enumerate(cat_indices):
            encoding[j] = 5 - i  # Higher weight for higher-ranked categories
        return encoding

    def build_embeddings(self):        
        # Build and normalize expertise embeddings for all speakers
        self.expertise_embedding = np.array([
            self.weighted_encoding([
                kw.strip() for kw in row['expertise_topics'].split(',') if kw.strip() in self.categories
            ]) for _, row in self.df.iterrows()
        ])
        self.expertise_embedding = normalize(self.expertise_embedding, axis=1)
        
        # Build and normalize the topic embedding
        self.topic_weighted_embedding = self.weighted_encoding(self.top_categories)
        print('Topic weighted embedding:', self.topic_weighted_embedding)
        self.query_vec = np.array(self.topic_weighted_embedding, dtype=np.float32).reshape(1, -1)
        self.query_vec = normalize(self.query_vec, axis=1)

    def recommend(self, k=5):
        # Build a FAISS index and perform similarity search
        index = faiss.IndexFlatL2(len(self.categories))
        index.add(self.expertise_embedding)
        D, I = index.search(self.query_vec, k)
        print('Top', k, 'similar speaker indices:', I[0])
        print('Distances:', D[0])
        print(self.df.iloc[I[0]])
        return self.df.iloc[I[0]]

if __name__ == "__main__":
    # Define categories and topic
    categories = ['AI', 'technology', 'innovation', 'business', 'leadership', 'education', 'science', 'healthcare', 'wellness', 'arts', 'culture', 'sports',
                  'entertainment', 'social impact', 'lifestyle']
    topic = 'Setting the Scene: How Storytelling and Representation in the Media Shapes Culture and Identity'
    # Create and run the recommender
    recommender = SpeakerRecommender('speakers.csv', categories, topic)
    recommender.build_embeddings()
    recommender.recommend(k=5)