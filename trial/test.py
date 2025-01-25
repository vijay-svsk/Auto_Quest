import google.generativeai as genai
import json
from db import init_main_database, get_only_questions_based_on_fileid_from_main_db, insert_academic_standard_to_main_db

# Configure the API key for Gemini (Google Generative AI)
genai.configure(api_key='AIzaSyDvpbV34TFp2hGXWF5Hl9zONjlKeKoAuv8')

# Initialize the model (Gemini)
model = genai.GenerativeModel('gemini-1.5-flash')

def classify_questions_to_academic_standards(questions_list, academic_standards):
    prompt = f"""
    I have a list of questions and a list of academic standards. I need you to classify each question into the most relevant academic standard based on its content. 
    Here are the academic standards: {academic_standards}
    Here are the questions: {questions_list}
    For each question, analyze its content and context to determine the best matching academic standard from the list. Give only L1,L2,L3,L4,L5, dont give full name. 
    The output should be a JSON object must be in the following format:
    [
        {{
            "id": "1",
            "question": "question1",
            "academic_standard": "L1"
        }},
        {{
            "id": "2",
            "question": "question2",
            "academic_standard": "L2"
        }}
    ]
    """
    
    response = model.generate_content([prompt])
    print("Raw response:", response.text)  # Debugging step
    return response.text

# List of academic standards
academic_standards = [
    "Problem Solving - L1",
    "Reasoning & Proof - L2",
    "Communication - L3",
    "Connections - L4",
    "Visualization & Representation - L5"
]

# Retrieve the list of questions from the database
questions_list = get_only_questions_based_on_fileid_from_main_db("1")

if not questions_list:
    print("Error: No questions retrieved from the database.")
else:
    # Call the function to classify questions into academic standards
    response_str = classify_questions_to_academic_standards(questions_list, academic_standards)

    if response_str:
        try:
            # print("Response string:", response_str)  # Debugging step

            # Remove the markdown block (```json and ```)
            formatted_str = response_str.strip("```json\n").strip("```")
            # print(type(formatted_str))
            # Parse the string into a JSON object
            json_obj = json.loads(formatted_str)

            # Extract id, question, and academic_standard
            for item in json_obj:
                question_id = item.get("id")
                academic_standard = item.get("academic_standard")

                if question_id and academic_standard:
                    # Print or process the extracted data
                    print(f"ID: {question_id}")

                    print(f"Academic Standard: {academic_standard}")
                    print("-" * 40)

                    # Insert the results into the database (add a column for academic standards)
                    insert_academic_standard_to_main_db(question_id, academic_standard)
                else:
                    print(f"Missing data in item: {item}")

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
    else:
        print("Error: No response from the Generative AI API.")