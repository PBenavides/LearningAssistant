
import tiktoken
import json
#assistant
from assistant.processes.flashcard_generator.prompts import (
    SYSTEM_QUESTION_GENERATOR_PROMPT,
    JSON_SCHEMAS,
    PARSING_PROMPT
)

from assistant.utils import write_string_to_file, get_files_content
from assistant.models.base import chat_completion

#Get the encoding
encoding = tiktoken.get_encoding("cl100k_base")

#Generate questions over the files input
def generate_questions(topic_name, file_content):
    #Parse topic_name
    end_topic_name = ''.join(topic_name.split('-')[1:])

    #format the json schema
    json_schema = ','.join([f"'{key}':'{value}'"for key, value in JSON_SCHEMAS["questions_schema"].items()])

    messages=[
        {
        "role":"system",
        "content":SYSTEM_QUESTION_GENERATOR_PROMPT.format(
            topic_name=end_topic_name,
            json_schema=json_schema,
            agent_supervisor_guidelines=""
        )
        },
        {
        "role":"user",
        "content": file_content
        }
    ]

    num_tokens_system = len(encoding.encode(messages[0]["content"]))
    num_tokens_user = len(encoding.encode(messages[1]["content"]))

    print(f"Number of tokens system: {num_tokens_system}")
    print(f"Number of tokens user's file-content: {num_tokens_user}")

    response = chat_completion(
        model='gpt-3.5-turbo',
        messages=messages,
        response_format={"type":"json_object"}
        )

    num_output_tokens = len(encoding.encode(response.choices[0].message.content))
    print(f"Number of tokens output: {num_output_tokens}")

    return response.choices[0].message.content

def parse_and_write_questions(json_string_questions, output_path):
    """This function parse the json string and write the questions to a file.
    """
    try:
        questions = json.loads(json_string_questions)["questions"]

    except Exception as e:
        print(f"Error parsing the json: {json.loads(json_string_questions)}")
        questions = json.loads(json_string_questions)["question"]

    deck_name = 'VPC_AND_MEMORY'

    for question_answer in questions:

        question = question_answer["question"]
        answer = question_answer["answer"]
        level = question_answer["level"]
        topic = question_answer["topic"]

        #Parse the question with the required format
        parsed_question = PARSING_PROMPT.format(
            question=question,
            answer=answer,
            level=level,
            topic=topic,
            deck=deck_name
        )
        #Write
        write_string_to_file(f"{output_path}/ANKI_NEW_AWS_FORMAT.md", parsed_question)

    print('Done!')

def FlashcardGenerator(PATH_TO_OBSIDIAN, OUTPUT_PATH):

    file_contents = get_files_content(PATH_TO_OBSIDIAN)
    
    for topic_name, file_content in file_contents.items():
        #Generate questions
        json_string_questions = generate_questions(topic_name, file_content)

        #Parse and write questions
        parse_and_write_questions(json_string_questions, OUTPUT_PATH)

    print('All files have been parsed and written to ANKI_AWS_QUESTIONS.md')