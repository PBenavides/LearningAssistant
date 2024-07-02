"""Thinking Process of the LLM:

LLM(1): Question Maker. Foundational Knowledge & Comprehension.
1.- Propose question-answers based on the main concepts.
2.- Write the questions and answers in required format.
3.- Validate format.

LLM(2): Case Maker. Application & Analysis.
1.- Propose a practical case based on the main concepts.
2.- Write the case in required format.
3.- Validate format.

LLM(3): Evaluation of quality
1.- Evaluate the quality of the questions and answers.
2.- Evaluate the quality of the practical case.
3.- Evaluate the quality of the format.

LLM(4): Agent Supervisor
1.- Reads and Diagnose user's knowledge based on feedback and form-answers
2.- Gives guidelines to the agent to focus on more specific topics or goals.

LLM(3) -> Rewrites and provide guidelines to LLM(1) and LLM(2).
LLM(4) -> Define focus and provide guidelines to LLM(1) and LLM(2).

---------------- Proposals ----------------
Form maker:
LLM(5): Form Maker. Foundational Knowledge & Comprehension.
- Creates a form to evaluate the user's knowledge based on the questions and answers.
- Evaluates user's responses to the form.
- Creates a report over points of improvement or to move into the next topic.
"""

from assistant.processes.flashcard_generator.generator import FlashcardGenerator
from settings import PATH_TO_OBSIDIAN, OUTPUT_PATH_ANKI_GENERATED_CARDS

from dotenv import load_dotenv
load_dotenv()

#Print the files
if __name__ == '__main__':
    
    FlashcardGenerator(PATH_TO_OBSIDIAN, OUTPUT_PATH_ANKI_GENERATED_CARDS)

    print('All files have been parsed and written to ANKI_AWS_QUESTIONS.md')