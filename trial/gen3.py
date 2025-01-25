

import google.generativeai as genai
import json
import re
from db import get_only_questions_based_on_fileid_from_main_db ,insert_chapters_to_main_db
import typing_extensions as typing

# Configure the API key for Gemini (Google Generative AI)
genai.configure(api_key='AIzaSyDvpbV34TFp2hGXWF5Hl9zONjlKeKoAuv8')

# Initialize the model (Gemini)
model = genai.GenerativeModel('gemini-1.5-flash')



def assign_chapters_to_questions(questions_list, chapter_list):
   
    prompt = """
    I have a list of questions and a list of chapters. I need you to assign the most relevant chapter name from the provided chapter list to each question. 
    Here are the chapters: `""" + str(chapter_list) + """` , Here are the questions: `""" + str(questions_list) + """`, 
    For each question, analyze its content and context to determine the best matching chapter from the chapter list. The assigned chapter must be one of the provided chapters. Do not create or suggest new chapters.
    The output should be a JSON object in the following format:
      [
        {
            "id": "1",
            "question": "question1",
            "chapter": "Chapter X - Chapter Name"
        },
        {
            "id": "2",
            "question": "question2",
            "chapter": "Chapter Y - Chapter Name"
        }
    ]  

    """

    response = model.generate_content([prompt])
    return response.text


chapter_list = [
    "Chapter 1 - Real Numbers",
    "Chapter 2 - Sets",
    "Chapter 3 - Polynomials",
    "Chapter 4 - Pair of Linear Equations in Two Variables",
    "Chapter 5 - Quadratic Equations",
    "Chapter 6 - Progressions",
    "Chapter 7 - Coordinate Geometry",
    "Chapter 8 - Similar Triangles",
    "Chapter 9 - Tangents and Secants to a Circle",
    "Chapter 10 - Mensuration",
    "Chapter 11 - Trigonometry",
    "Chapter 12 - Applications of Trigonometry",
    "Chapter 13 - Probability",
    "Chapter 14 - Statistics"
]
questions_list = get_only_questions_based_on_fileid_from_main_db("1")

# print(questions_list)

response_dict=assign_chapters_to_questions(questions_list,chapter_list)

# print(response_dict)
# Remove the markdown block (```json and ```)
formatted_str = response_dict.strip("```json\n").strip("```")
# print(type(formatted_str))
# Parse the string into a JSON object
json_obj = json.loads(formatted_str)

# Print the resulting JSON object
print(json_obj)

# Extract `id`, `question`, and `chapter`
for item in json_obj:
    question_id = item["id"]
    question_text = item["question"]
    chapter_name = item["chapter"]

    # Print or process the extracted data
    # print(f"ID: {question_id}")
    # print(f"Question: {question_text}")
    # print(f"Chapter: {chapter_name}")
    # print("-" * 40)

    insert_chapters_to_main_db(question_id,question_text,chapter_name)








