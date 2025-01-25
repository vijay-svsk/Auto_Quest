import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def transfer_and_sort_data(source_db="main.db", target_db="sorted.db"):
    """
    Transfers and sorts data from the source database to a new sorted database.

    Args:
        source_db (str, optional): Path to the source SQLite database (default: "main.db").
        target_db (str, optional): Path to the new sorted database (default: "sorted.db").

    Returns:
        list: A list of sorted data rows from the source database.
    """

    # Connect to the source and target databases (create target_db if it doesn't exist)
    try:
        source_conn = sqlite3.connect(source_db)
        source_cur = source_conn.cursor()
        target_conn = sqlite3.connect(target_db)
        target_cur = target_conn.cursor()
    except sqlite3.OperationalError:
        # Create the target database if it doesn't exist
        print(f"Creating new sorted database: '{target_db}'")
        target_conn = sqlite3.connect(target_db)
        target_cur = target_conn.cursor()

    # Enable foreign keys in the target database
    target_cur.execute("PRAGMA foreign_keys = ON;")

    # Create tables in the target database (if they don't exist already)
    target_cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filetype TEXT,
            filepath TEXT,
            upload_time TEXT
        );
    """)

    target_cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class TEXT NOT NULL,
            subject TEXT NOT NULL,
            assessment TEXT NOT NULL,
            marks INTEGER NOT NULL,
            chapter TEXT,
            question_text TEXT NOT NULL,
            file_id INTEGER,
            similarity REAL,
            FOREIGN KEY (file_id) REFERENCES files(id)
        );
    """)

    target_conn.commit()

    # Fetch all questions from the source database for similarity computation
    question_texts = []
    source_cur.execute("SELECT question_text FROM questions")
    for row in source_cur.fetchall():
        question_texts.append(row[0])

    # Compute the TF-IDF matrix if there are questions
    if question_texts:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(question_texts)
    else:
        tfidf_matrix = None

    # Fetch and sort data from the source database
    source_cur.execute("""
        SELECT
            q.id, q.class, q.subject, q.assessment, q.marks, q.chapter,
            q.question_text, q.file_id, f.filename, f.filetype, f.filepath, f.upload_time
        FROM questions q
        LEFT JOIN files f ON q.file_id = f.id
        ORDER BY q.class ASC, q.subject ASC, q.chapter ASC, q.assessment ASC, q.marks ASC, q.question_text ASC;
    """)
    sorted_data = source_cur.fetchall()

    # Map for file_id mapping between source and target databases
    file_id_map = {}

    for i, row in enumerate(sorted_data):
        source_file_id = row[7]  # Original file_id from source
        if source_file_id is not None and source_file_id not in file_id_map:
            # Insert the file data into the target database if not already mapped
            target_cur.execute("""
                INSERT INTO files (filename, filetype, filepath, upload_time)
                VALUES (?, ?, ?, ?);
            """, (row[8], row[9], row[10], row[11]))
            new_file_id = target_cur.lastrowid
            file_id_map[source_file_id] = new_file_id

        target_file_id = file_id_map.get(source_file_id)

        # Compute similarity for the current question
        similarity = None
        if tfidf_matrix is not None and tfidf_matrix.shape[0] > 1:
            similarity_scores = cosine_similarity(tfidf_matrix[i], tfidf_matrix)
            similarity = np.mean(similarity_scores)

        # Insert the question data into the target database
        target_cur.execute("""
            INSERT INTO questions (class, subject, assessment, marks, chapter, question_text, file_id, similarity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (row[1], row[2], row[3], row[4], row[5], row[6], target_file_id, similarity))

    # Commit changes and close connections
    target_conn.commit()
    source_conn.close()
    target_conn.close()

    print("Data transferred and sorted successfully into 'sorted.db'.")
    return sorted_data


# Main Execution
sorted_data = transfer_and_sort_data()