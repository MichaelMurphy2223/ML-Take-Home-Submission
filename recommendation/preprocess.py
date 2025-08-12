import pandas as pd
from sentence_transformers import SentenceTransformer, util

class Preprocessor:
    def __init__(self, input_csv, output_csv):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.categories = ['AI', 'technology', 'innovation', 'business', 'leadership', 'education', 'science', 'healthcare', 'wellness', 'arts', 'culture', 'sports',
            'entertainment', 'social impact', 'lifestyle']
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.category_embeddings = self.model.encode(self.categories, convert_to_tensor=True)
        self.df = None

    def load_data(self):
        self.df = pd.read_csv(self.input_csv)

    def preprocess(self):
        self.df['expertise_topics'] = self.df.apply(lambda x: f"{x['title']} {x['background']} {x['experience']} {x['keywords']}", axis=1)
        self.df['name'] = self.df.apply(lambda x: f"{x['first_name']} {x['last_name']}", axis=1)
        self.df.drop_duplicates(inplace=True)
        self.df['title'].dropna(inplace=True)
        self.df = self.df[['name', 'title', 'expertise_topics']]
        self.df.reset_index(drop=True, inplace=True)

    def extract_topics(self, keywords):
        topic_embedding = self.model.encode(keywords, convert_to_tensor=True)
        similarity_scores = util.pytorch_cos_sim(topic_embedding, self.category_embeddings)[0]
        top_categories = [self.categories[i] for i in similarity_scores.argsort(descending=True)[:5]]
        return top_categories

    def apply_topic_extraction(self):
        self.df['expertise_topics'] = self.df['expertise_topics'].apply(lambda x: ",".join(self.extract_topics(x)))

    def save(self):
        self.df.to_csv(self.output_csv, index=False)

if __name__ == "__main__":
    preprocessor = Preprocessor('ml_interview_dataset_20250804_095938.csv', 'speakers.csv')
    preprocessor.load_data()
    preprocessor.preprocess()
    preprocessor.apply_topic_extraction()
    preprocessor.save()