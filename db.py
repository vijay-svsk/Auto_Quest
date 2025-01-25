# db.py

import sqlite3
from datetime import datetime
import os

def init_main_database():
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
     # Enable foreign key constraints (required for SQLite)
    cur.execute("PRAGMA foreign_keys = 1;")
    cur.execute('''CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filetype TEXT,
            filepath TEXT,
            upload_time TEXT NOT NULL ,
            user_id INTEGER,  -- Foreign key column
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE -- Foreign key constraint
        )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class TEXT NOT NULL,
            subject TEXT NOT NULL,
            assessment TEXT NOT NULL,
            marks INTEGER NOT NULL,
            chapter TEXT,
            question_text TEXT NOT NULL,
            diagram TEXT,
            standard TEXT,
            file_id INTEGER,  -- Foreign key column
            user_id INTEGER,  -- Foreign key column 
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE ,  -- Foreign key constraint
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE -- Foreign key constraint
        )
    ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS questionpapers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class TEXT NOT NULL,
            subject TEXT NOT NULL,
            assessment TEXT NOT NULL,
            sections TEXT NOT NULL,
            created_time TEXT NOT NULL,
            user_id INTEGER,  -- Foreign key column
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE -- Foreign key constraint
        )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS generatedquestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            chapter TEXT,
            sectionid TEXT,
            marks INTEGER NOT NULL,
            diagram TEXT,
            standard TEXT,
            paper_id INTEGER,  -- Foreign key column
            FOREIGN KEY (paper_id) REFERENCES questionpapers(id) ON DELETE CASCADE -- Foreign key constraint
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS teacher_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT,
            subject_name TEXT,
            feedback_percentage REAL,
            class_name TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL ,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            designation TEXT ,
            qualification TEXT,
            classTeacher TEXT
        )
        ''')

    # Insert sample users
    # cur.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
    #             ('admin', 'admin', 'admin'))
    conn.commit()
    conn.close()


def add_admin_user():
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
# Check if the admin user already exists
    cur.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    admin_count = cur.fetchone()[0]
    
    if admin_count == 0:
        # If no admin exists, insert a new one
        cur.execute('INSERT INTO users (username, password, role,designation, qualification, classTeacher) VALUES (?, ?, ?,?, ?, ?)', 
                    ('admin', 'admin', 'admin','principal','principal','principal' ))
        conn.commit()
        print("Admin user added successfully.")
    else:
        print("Admin user already exists, skipping insertion.")
    conn.close()



# Function to get a user by username
def get_user_by_username(username):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    user = cur.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    user = cur.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_files_uploaded_count(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    # Query to count the number of files uploaded by the user
    count = cur.execute('SELECT COUNT(*) FROM files WHERE user_id = ?', (user_id,)).fetchone()[0]
    conn.close()
    return count


def get_questionpapers_count(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    # Query to count the number of question papers created by the user
    count = cur.execute('SELECT COUNT(*) FROM questionpapers WHERE user_id = ?', (user_id,)).fetchone()[0]
    conn.close()
    return count


# Function to add a new user
def add_user(username, password, role,designation, qualification, classTeacher):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO users (username, password, role , designation, qualification, classTeacher) VALUES (?, ?, ?,?, ?, ?)',
                 (username, password, role,designation, qualification, classTeacher))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    users = cur.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

def edit_user_based_on_id(username, password, role, designation, qualification, class_teacher, user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    # Update user in the database
    cur.execute('''UPDATE users SET username = ?, password = ?, role = ?, 
                    designation = ?, qualification = ?, classTeacher = ? 
                    WHERE id = ?''', 
                (username, password, role, designation, qualification, class_teacher, user_id))

    conn.commit()
    conn.close()

def delete_user_based_on_id(user_id):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    # Delete user from the database
    cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def save_file_to_main_db(filename, filetype, filepath,userid):

    # Get the current timestamp in ISO 8601 format (YYYY-MM-DD HH:MM:SS)
    upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    

    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO files (filename, filetype, filepath, upload_time,user_id) VALUES (?, ?, ?, ?,?)',
                (filename, filetype, filepath, upload_time,userid))
    conn.commit()
    conn.close()

def get_file_id_by_filename(filename):
    # Connect to the SQLite database
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()

    # Execute the SELECT query to find the file by filename
    cur.execute('SELECT id FROM files WHERE filename = ?', (filename,))

    # Fetch the result
    result = cur.fetchone()

    # If the file was found, return the file ID
    if result:
        file_id = result[0]
    else:
        # If the file is not found, return None or an appropriate message
        file_id = None

    # Close the connection
    conn.close()

    return file_id
 

def delete_file_by_id(file_id):
    # Connect to the SQLite database to retrieve the file details
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()

    # Fetch the file details from the database (including the file path)
    cur.execute('SELECT  filepath FROM files WHERE id = ?', (file_id))
    result = cur.fetchone()

    if result:
        # Extract filename and file path from the query result
        file_path = result[0]

        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            # Delete the file from the filesystem
            os.remove(file_path)
            print(f"File deleted from filesystem.")
        else:
            print(f"File not found in the filesystem.")

        # Now delete the file record from the database
        cur.execute('DELETE FROM files WHERE id = ?', (file_id))
        conn.commit()
        print(f"File record with ID {file_id} deleted from the database.")
    else:
        print(f"File with ID {file_id} not found in the database.")

    # Close the database connection
    conn.close()


    
# init_main_database()
# save_file_to_main_db("sample file","pdf","uploads/SRPT SA-1 Maths Master.pdf","hello world")

def insert_question_to_main_db(class_name, subject, assessment, marks, question_text,file_id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    if check_question_exists_in_main_db(class_name, subject, assessment, marks, question_text):
        return

    cursor.execute('''INSERT INTO questions (class, subject, assessment, marks, question_text,file_id)
                      VALUES (?, ?, ?, ?, ?,?)''', (class_name, subject, assessment, marks, question_text,file_id))
    conn.commit()
    conn.close()

def insert_single_question_to_main_db(class_name, subject, assessment, marks, question_text,userid, diagram_path=None):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    if check_question_exists_in_main_db(class_name, subject, assessment, marks, question_text):
        return

    cursor.execute('''INSERT INTO questions (class, subject, assessment, marks, question_text,diagram,user_id,file_id)
                      VALUES (?, ?, ?, ?, ?,?,?,NULL)''', (class_name, subject, assessment, marks, question_text,diagram_path,userid))
    conn.commit()
    conn.close()

def check_question_exists_in_main_db(class_name, subject, assessment, marks, question_text):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM questions WHERE class=? AND subject=? AND assessment=? AND marks=? AND question_text=?''',
                   (class_name, subject, assessment, marks, question_text))
    existing_question = cursor.fetchone()
    conn.close()
    return existing_question

def get_all_files_from_main_db():
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM files''')
    all_files = cursor.fetchall()
    conn.close()
    # print(all_files)
    return all_files

def get_all_files_based_on_userid_from_main_db(user_id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM files WHERE user_id=?''',
                   ( user_id,))
    all_question = cursor.fetchall()
    conn.close()
    return all_question



def get_all_questions_based_on_fileid_from_main_db(file_id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM questions WHERE file_id=?''',
                   ( file_id))
    all_question = cursor.fetchall()
    conn.close()
    return all_question


def get_question_based_on_id_from_main_db(id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM questions WHERE id=?''',
                   ( id,))
    question = cursor.fetchall()
    conn.close()
    return question


def get_all_questions_based_on_userid_from_main_db(user_id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM questions WHERE user_id=?''',
                   ( user_id,))
    all_question = cursor.fetchall()
    conn.close()
    return all_question

def get_all_questions_with_all_userids_from_main_db():
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    
    # Fetch only questions that have a non-null user_id
    cursor.execute('''SELECT * FROM questions WHERE user_id IS NOT NULL''')
    
    all_questions = cursor.fetchall()
    conn.close()
    return all_questions

def get_only_questions_based_on_fileid_from_main_db(file_id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT id,question_text FROM questions WHERE file_id=?''',
                   ( file_id))
    all_question = cursor.fetchall()
    conn.close()
    return all_question

def insert_chapters_to_main_db(id , question,chapter):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE questions
        SET chapter = ?
        WHERE id = ?
    ''', (chapter,id))
    conn.commit()
    conn.close()


def insert_academic_standard_to_main_db(id ,standard):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE questions
        SET standard = ?
        WHERE id = ?
    ''', (standard,id))
    conn.commit()
    conn.close()


# Function to update the question in the database
def update_question_in_db(question_id, updated_data):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE questions
        SET class = ?, subject = ?, assessment = ?, marks = ?, question_text = ?,diagram = ?
        WHERE id = ?
    ''', (updated_data['class'], updated_data['subject'], updated_data['assessment'], updated_data['marks'], updated_data['question_text'],updated_data.get('diagram'), question_id))
    conn.commit()
    conn.close()




def get_dropdown_data():
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    
    # Fetch distinct values for class, subject, and assessment
    cur.execute("SELECT DISTINCT class FROM questions")
    classes = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT subject FROM questions")
    subjects = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT assessment FROM questions")
    assessments = [row[0] for row in cur.fetchall()]

    conn.close()
    return classes, subjects, assessments



def get_chapters(selected_class, selected_subject):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT DISTINCT chapter 
        FROM questions 
        WHERE class = ? AND subject = ? 
    ''', (selected_class, selected_subject))
    chapters = [row[0] for row in cur.fetchall()]
    conn.close()
    return chapters


def fetch_questions(class_name, subject, assessment, chapters, standards):
    """
    Fetch questions from the database based on the provided criteria.
    """
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    placeholders = ', '.join(['?'] * len(chapters))  # For multiple chapters
    standards_placeholders = ', '.join(['?'] * len(standards))
    query = f'''
        SELECT id, question_text, marks, chapter, standard 
        FROM questions 
        WHERE class = ? AND subject = ? AND assessment = ? 
        AND chapter IN ({placeholders}) 
        AND standard IN ({standards_placeholders})
    '''
    cursor.execute(query, (class_name, subject, assessment, *chapters, *standards))
    questions = cursor.fetchall()
    conn.close()
    return questions


# def distribute_questions_by_standard(questions, standard_distribution, total_questions):
#     """
#     Distribute questions based on standard preferences or randomly if not specified.
#     """
#     grouped_questions = {}
#     for question in questions:
#         standard = question[4]
#         if standard not in grouped_questions:
#             grouped_questions[standard] = []
#         grouped_questions[standard].append(question)

#     selected_questions = []
#     for standard, count in standard_distribution.items():
#         if standard in grouped_questions:
#             selected_questions.extend(grouped_questions[standard][:count])

#     remaining_questions = [
#         q for q in questions if q not in selected_questions
#     ]
#     if len(selected_questions) < int(total_questions):
#         selected_questions.extend(remaining_questions[:len(total_questions) - len(selected_questions)])
    
#     return selected_questions

def distribute_questions_by_standard(questions, standard_distribution, total_questions):
    """
    Distribute questions based on standard preferences, ensuring no over-selection occurs.
    """
    grouped_questions = {}
    for question in questions:
        standard = question[4]  # Assuming the standard is at index 4
        if standard not in grouped_questions:
            grouped_questions[standard] = []
        grouped_questions[standard].append(question)

    selected_questions = []
    remaining_questions = []
    
    # Select questions for each standard as per the distribution
    for standard, count in standard_distribution.items():
        if standard in grouped_questions:
            available_questions = grouped_questions[standard]
            # Select up to the requested number or the available number
            selected_questions.extend(available_questions[:count])
            # Add the remaining to the pool for later use
            remaining_questions.extend(available_questions[count:])

    # Add leftover questions to remaining_questions pool
    for standard, questions_list in grouped_questions.items():
        if standard not in standard_distribution:
            remaining_questions.extend(questions_list)

    # Fill up remaining slots if needed
    if len(selected_questions) < int(total_questions):
        slots_left = int(total_questions) - len(selected_questions)
        selected_questions.extend(remaining_questions[:slots_left])
    
    return selected_questions

def insert_generatedpaper_to_main_db(class_name, subject, assessment, sections, created_time,userid):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO questionpapers ( class, subject, assessment, sections, created_time,user_id)
                      VALUES (?, ?, ?, ?,?,?)''', (class_name, subject, assessment, sections, created_time,userid))
    conn.commit()
    
    # Retrieve the ID by selecting the last inserted record
    cursor.execute('SELECT id FROM questionpapers ORDER BY id DESC LIMIT 1')
    generated_paper_id = cursor.fetchone()[0]
    
    conn.close()
    
    return generated_paper_id



def insert_generatedquestion_to_main_db(question_text,chapter, sectionid, marks, standard_name , paper_id,diagram=None ):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO generatedquestions (question_text,chapter, sectionid, marks, diagram, standard,paper_id)
                      VALUES (?, ?, ?, ?, ?,?,?)''', (question_text,chapter, sectionid, marks, diagram, standard_name,paper_id))
    conn.commit()
    conn.close()



def get_all_papers_from_main_db():
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM questionpapers''')
    all_papers = cursor.fetchall()
    conn.close()
    # print(all_papers)
    return all_papers


def get_all_papers_based_on_userid_from_main_db(user_id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM questionpapers WHERE user_id=?''',
                   ( user_id,))
    all_question = cursor.fetchall()
    conn.close()
    return all_question


def get_all_questions_based_on_paperid_from_main_db(paper_id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM generatedquestions WHERE paper_id=?''',
                   ( paper_id))
    all_question = cursor.fetchall()
    conn.close()
    return all_question





# Function to update the question in the database
def replace_question_in_db(question_id, updated_data):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE generatedquestions
        SET  question_text = ?,diagram = ?
        WHERE id = ?
    ''', ( updated_data['question_text'],updated_data.get('diagram'), question_id))
    conn.commit()
    conn.close()


def delete_generatedpaper_from_db(paper_id):
    con = sqlite3.connect('main.db')
    cur = con.cursor()

    # Delete associated questions from generatedquestions
    cur.execute('DELETE FROM generatedquestions WHERE paper_id = ?', (paper_id,))
    
    # Delete the question paper
    cur.execute('DELETE FROM questionpapers WHERE id = ?', (paper_id,))
    
    con.commit()
    con.close()

def delete_questionpaper_from_db(paper_id):
    con = sqlite3.connect('main.db')
    cur = con.cursor()

    # Delete associated questions 
    cur.execute('DELETE FROM questions WHERE file_id = ?', (paper_id,))
    
    # Delete the question paper
    cur.execute('DELETE FROM files WHERE id = ?', (paper_id,))
    
    con.commit()
    con.close()

def delete_question_from_db(id):
    con = sqlite3.connect('main.db')
    cur = con.cursor()

    # Delete associated questions 
    cur.execute('DELETE FROM questions WHERE id = ?', (id,))
    
    con.commit()
    con.close()


def insert_teacherfeedback(teacher, subject, feedback_percentage, class_name):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO teacher_feedback (teacher_name, subject_name, feedback_percentage, class_name)
        VALUES (?, ?, ?, ?)
    ''', (teacher, subject, feedback_percentage, class_name))
    conn.commit()
    conn.close()


def get_teacherfeedback_from_main_db():
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM teacher_feedback''')
    data = cursor.fetchall()
    conn.close()
    return data