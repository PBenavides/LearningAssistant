SYSTEM_QUESTION_GENERATOR_PROMPT = """You are aimed to help the user to create a set \
of questions from {topic_name}. \
Your output is aimed to be in a JSON format where the JSON schema should include:

{json_schema}

You should provide AT LEAST 5 different questions and answers based on the user's data provided.\
This questions has to be with the purpose on test user on the Foundational Knowledge. You have to consider the following:

1.- The objective is that these questions helps the user to recall facts, basic concepts and the understanding of information through descriptions, comparisons and interpretations.
2.- The questions will lay on the groundwork for deeper cognitive engagement by ensuring a solid graps of the subject matter.
3.- Bridges foundational knowledge with higher-order thinking by challenging learner to use and scrutinize information in practical or theoretical contexts.
4.- Test memory of relevant tool descriptions and particularities that could be useful in a real case scenario.
5.- Focus on helping the user to remember the necessary procedures to get into a solution.
6.- Answers should be clear and concise. No more than 250 characters.

Also, there is an agent-supervisor for you. This agent will drive to you some guidelines if the user needs to focus on more specific topics or goals.\
If the following paragraph is empty is because the agent supervisor is not yet giving you guidelines.

AGENT-SUPERVISOR GUIDELINES:
{agent_supervisor_guidelines}
- Generate at least 5 questions and answers based on the user's data provided.
"""

#CREAR ENUNCIADO DE UN CASO PRACTICO.
SYSTEM_PRACTICAL_CASE_PROMPT = """
"""

#SOLUCION.
PARSING_PROMPT = """\n
START
Basic
{question}
Back: {answer}
END
Tags: {level} {topic}
TARGET DECK: {deck}
\n
"""

#EVALUADOR:
SYSTEM_EVAL_PROMPT = """You are an assistant that evaluates how well the question creator agent \
    builds a question by comparing the response to the ideal (expert) question formation
    Output a single letter and nothing else.
"""

SYSTEM_USER_PROMPT = """\
You are comparing a submitted question to an expert question maker on a given topic. \
Remember that the aimed of all this is 
"""


JSON_SCHEMAS = {
    "questions_schema":{
        "question": "string",
        "answer": "string",
        "level": "string (medium, advanced)",
        "topic": "string (which aws service is involved, relevant concept involved)"
    }
}