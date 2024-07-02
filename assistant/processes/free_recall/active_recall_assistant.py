"""RAG based calling generator.

Remember that the steps for RAG systems are:

- Rewrite
- Retrieve
- Rerank
- Refine
- Fuse
- Generate

--- 
Steps over the thinking process of this assistant.

1.- Rewrite the user's recall document to a more specific document.
2.- Infer error based on retrieval concepts related with the topic of interest.
3.- Rerank the errors based on the importance of the topic.
4.- Refine the errors to be more specific and explain the process
5.- Generate the response and correction with highlights for the user.

"""
import tiktoken
import json
import os

from assistant.processes.free_recall.prompts import (
    SYSTEM_FREE_RECALL_REWRITER_PROMPT,
    SYSTEM_FREE_RECALL_FEEDBACK_PROMPT
)

from assistant.utils import write_string_to_file, get_item_from_dynamodb
from assistant.models.base import chat_completion, regular_straight_call

#Get the encoding
encoding = tiktoken.get_encoding("cl100k_base")
api_key = os.environ['OPENAI_API_KEY']

def free_recall_step_0(
):
    """
    Load Student Objectives, Guidelines and topics.
    """

    step_0_dict = {

    }

    return step_0_dict

def free_recall_step_1(
        path_to_user_file: str,
        user_content: str,
        user_topic: str
):

    #Get previous guidelines
    previous_guidelines = get_item_from_dynamodb(
        table_name='FreeRecallTestGuidelines',
        key='user-topic-latest-guidelines',
        value='1_ec2_29_03_11'
    )

    rewritten_document = regular_straight_call(
        system_prompt=SYSTEM_FREE_RECALL_REWRITER_PROMPT,
        user_content=user_content,
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=2000,
        response_format=None
    )

    feedback_document = regular_straight_call(
        system_prompt=SYSTEM_FREE_RECALL_FEEDBACK_PROMPT.format(
            weaknesses_guidelines=previous_guidelines['weaknesses'],
            strengths_guidelines=previous_guidelines['strengths']
        ),
        user_content=rewritten_document,
        model='gpt-3.5-turbo',
        temperature=0,
        response_format=None
    )

    write_string_to_file(path_to_user_file+f'{user_topic}.md', rewritten_document)
    write_string_to_file(path_to_user_file+f'{user_topic}_feedback.md', feedback_document)

    return rewritten_document, feedback_document