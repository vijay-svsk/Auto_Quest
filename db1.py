from flask import Flask, render_template, request
import sqlite3
from sentence_transformers import SentenceTransformer, util
from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

DATABASE = 'main.db'
MODEL_NAME = 'all-mpnet-base-v2'
BERT_MODEL_NAME = "bert-base-uncased"

app = Flask(__name__)

# Load SentenceTransformer and BERT
sentence_model = SentenceTransformer(MODEL_NAME)
bert_tokenizer = BertTokenizer.from_pretrained(BERT_MODEL_NAME)
bert_model = BertModel.from_pretrained(BERT_MODEL_NAME)

def preprocess_with_bert(text):
    """Tokenize text using BERT tokenizer."""
    inputs = bert_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    return inputs

def get_bert_embeddings(text):
    """Get BERT embeddings for the text."""
    inputs = preprocess_with_bert(text)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze(0)
    return embeddings.numpy()

def get_questions_from_db():
    """Fetch questions from the database."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(questions)")
        columns = [row[1] for row in cursor.fetchall()]

        required_columns = ["id", "question_text", "class", "subject", "lesson", "marks", "l1", "l2", "l3", "l4", "l5"]
        available_columns = [col for col in required_columns if col in columns]
        select_statement = "SELECT " + ", ".join(available_columns) + " FROM questions"
        cursor.execute(select_statement)
        questions = cursor.fetchall()

        conn.close()
        return questions, available_columns
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return [], []

def rank_questions_by_sentence_transformer(questions, available_columns):
    """Rank questions using SentenceTransformer embeddings."""
    if not questions:
        return []

    question_texts = [q[available_columns.index("question_text")] for q in questions if "question_text" in available_columns]
    question_embeddings = sentence_model.encode(question_texts)

    centrality_scores = []
    for emb1 in question_embeddings:
        similarities = util.cos_sim(emb1, question_embeddings)
        avg_similarity = similarities.sum() / len(question_embeddings)
        centrality_scores.append(avg_similarity.item())

    combined_scores = []
    for i, question in enumerate(questions):
        combined_score = centrality_scores[i]
        combined_scores.append((question, combined_score))

    combined_scores.sort(key=lambda x: x[1], reverse=True)
    return combined_scores

def rank_questions_with_bert(query_text):
    """Rank questions using BERT embeddings based on similarity to query text."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, question_text FROM questions")
        questions = cursor.fetchall()

        query_embedding = get_bert_embeddings(query_text)
        ranked_questions = []

        for question_id, question_text in questions:
            question_embedding = get_bert_embeddings(question_text)
            similarity_score = cosine_similarity(query_embedding.reshape(1, -1), question_embedding.reshape(1, -1))[0][0]
            ranked_questions.append((question_id, question_text, similarity_score))

        ranked_questions.sort(key=lambda x: x[2], reverse=True)
        return ranked_questions
    except Exception as e:
        print(f"Error in BERT ranking: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_dropdown():
    """Fetch distinct values for dropdowns."""
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT class FROM questions")
    classes = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT DISTINCT subject FROM questions")
    subjects = [row[0] for row in cur.fetchall()]
    conn.close()
    return classes, subjects


@app.route("/", methods=["GET", "POST"])
def index():
    classes, subjects = get_dropdown_data()
    ranked_questions = []
    query_ranked_questions = []

    if request.method == "POST":
        selected_class = request.form.get("class")
        selected_subject = request.form.get("subject")
        query_text = request.form.get("query_text")

        questions, available_columns = get_questions_from_db()
        filtered_questions = [q for q in questions if q[available_columns.index("class")] == selected_class and q[available_columns.index("subject")] == selected_subject]

        if filtered_questions:
            ranked_questions = rank_questions_by_sentence_transformer(filtered_questions, available_columns)

        if query_text:
            query_ranked_questions = rank_questions_with_bert(query_text)

    return render_template("index.html", classes=classes, subjects=subjects, ranked_questions=ranked_questions, query_ranked_questions=query_ranked_questions)

if __name__ == "__main__":
    app.run(debug=True)
