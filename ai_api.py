from flask import Flask, request, jsonify
from postgre import PostgreConnector
import re
import pandas as pd
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer
from hdbscan import HDBSCAN
from umap import UMAP
from sentence_transformers import SentenceTransformer
from bertopic.representation import TextGeneration
from transformers import pipeline
from bertopic import BERTopic
import numpy as np
import random
import torch

SEED = 42
np.random.seed(SEED)
random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

app = Flask(__name__)

def preprocess_text(text):
    """Remove URLs and non-alphabetic characters, then convert to lowercase."""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    return text

@app.route('/model', methods=['POST'])
def model():
    """Handle POST requests for topic modeling."""
    torch.cuda.empty_cache()
    print(request)
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    platform = data.get('platform')
    subtopic = data.get('subtopic')
    days = data.get('days')

    if platform not in ['silver_reddit', 'silver_stack_exchange']:
        return jsonify({"error": "Invalid platform"}), 400

    sql = PostgreConnector()
    sql.init_sql()
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    query = f"SELECT * FROM {platform} WHERE TOPIC = '{subtopic}' AND TIMESTAMP_UTC BETWEEN '{start_time}' AND '{end_time}'"
    data = sql.query_with_sql_command(query)

    titles_and_dates = extract_titles_and_dates(data, platform)
    titles = titles_and_dates['TITLE'].tolist()

    len_docs = len(titles)

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device=0)
    embeddings = embedding_model.encode(titles, show_progress_bar=True)
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.1, metric='cosine', random_state=SEED)
    hdbscan_model = HDBSCAN(min_cluster_size=max(1, len_docs // 80), metric='euclidean')
    vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(2, 3))

    prompt = """
    I have topic that contains the following documents: \n[DOCUMENTS] \n
    The topic is described by the following keywords: [KEYWORDS] \n

    Based on the above information, can you give a short label of the topic?
    """

    generator = pipeline('text2text-generation', model='google/flan-t5-base', device=0, temperature=0)
    generator = TextGeneration(generator, prompt=prompt)

    representation_model = {"TextGeneration": generator}

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        representation_model=representation_model,
        top_n_words=10
    )

    topics, probs = topic_model.fit_transform(titles, embeddings)

    custom_label = topic_model.get_topic_info()['TextGeneration'].str[0].fillna('').tolist()
    custom_label[0] = 'other'
    topic_model.set_topic_labels(custom_label)

    doc_info = topic_model.get_document_info(titles)
    doc_info = enrich_doc_info(doc_info, titles_and_dates, start_time, end_time, subtopic)
    
    sql.insert_to_table(table_name="reddit_topic_modeling" if platform == 'silver_reddit' else "stack_exchange_topic_modeling", df=doc_info, schema='public')
    return jsonify({"message": "Data processed and inserted successfully"}), 200

def extract_titles_and_dates(data, platform):
    """Extract and preprocess titles and dates based on the platform."""
    if platform == 'silver_reddit':
        titles_and_dates = data[['ID', 'TITLE', 'TIMESTAMP_UTC']]
    else:
        titles_and_dates = data[['QUESTION_ID', 'TITLE', 'TIMESTAMP_UTC']]
    titles_and_dates['TITLE'] = titles_and_dates['TITLE'].apply(preprocess_text)
    return titles_and_dates

def enrich_doc_info(doc_info, titles_and_dates, start_time, end_time, subtopic):
    """Add additional information to the document info DataFrame."""
    doc_info['start_time'] = start_time
    doc_info['end_time'] = end_time
    doc_info['created_time'] = pd.to_datetime(titles_and_dates['TIMESTAMP_UTC'])
    doc_info['topic_original'] = subtopic
    doc_info = doc_info[['Document', 'CustomName', 'start_time', 'end_time', 'created_time', 'topic_original']]
    doc_info.rename(columns={'Document': 'title', 'CustomName': 'cluster_topic_modeling'}, inplace=True)
    return doc_info


# {
#     "platform": "silver_reddit",
#     "subtopic": "reddit_futurology",
#     "days": 30
# }
# {
#     "platform": "silver_stack_exchange",
#     "subtopic": "stack_over_flow",
#     "days": 30
# }
if __name__ == '__main__':
    app.run(debug=True)