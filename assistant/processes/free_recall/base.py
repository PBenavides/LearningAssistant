import boto3
from boto3.dynamodb.conditions import Key
import asyncio
import logging
import json
import os
from typing import Any, List, Dict

from settings import boto3_configuration

from assistant.models.openai_base import OpenAIModel
from assistant.utils import write_string_to_file
from assistant.processes.free_recall.prompts import (
    SYSTEM_FREE_RECALL_REWRITER_PROMPT,
    SYSTEM_FREE_RECALL_FEEDBACK_PROMPT,
    SYSTEM_FREE_RECALL_GENERATE_GUIDELINES_PROMPT
)

boto3.setup_default_session(**boto3_configuration)

class FreeRecallAssistant:
    def __init__(self, user_id: str, topic: str):
        self.user_id = user_id
        self.meta_topic = None
        self.sub_topic = None
        self.topic = topic
        self.topic_id = '1'
        self.api_key = os.environ['OPENAI_API_KEY']
        self.step_num = 0
        self.table_name='FreeRecallData'
        self.primary_key = 'UserId_TopicId_TS'
        self.user_topic_key = '1_1_2'

    def first_step(self, user_content: str) -> Any:
        """
        """

        #HARD CODE FOR NOW
        self.guidelines_last_run = self._get_latest_user_topic_data(
            table_name=self.table_name,
            user_topic_key=self.user_topic_key
        )

        if self.guidelines_last_run is None:

            self.guidelines_last_run = {
                'json_guidelines': {
                    'weaknesses': " ",
                    'strengths': " "
                }
            }

            print(f"Guidelines are from a new object!")

        rewriter_model = OpenAIModel(api_key=self.api_key, model='gpt-3.5-turbo')
        rewriter_model.set_system_prompt(SYSTEM_FREE_RECALL_REWRITER_PROMPT)

        feedback_model = OpenAIModel(api_key=self.api_key, model='gpt-3.5-turbo')
        feedback_model.set_system_prompt(SYSTEM_FREE_RECALL_FEEDBACK_PROMPT.format(
            weaknesses_guidelines=self.guidelines_last_run['json_guidelines']['weaknesses'],
            strengths_guidelines=self.guidelines_last_run['json_guidelines']['strengths']
        ))

        #RUNS:
        self.rewritten_document = rewriter_model.run(user_content=user_content)

        #This has to be build for the last iteraiton.
        self.feedback_document = feedback_model.run(user_content=user_content)
        self.step_num += 1

        return self.rewritten_document, self.feedback_document

    def second_step(self):
        """
        In-bound and out-bound Feedback retrieved information.
        RAG System.
        """
        return 0

    def third_step(self, rewritten_document: str) -> Dict[str, Any]:
        """
        Generate guidelines for the user based on the user document and the previous guidelines.
        Assessing the question: How much has the user accomplished the previous guidelines?

        Output:
        json_guidelines: {
            "weaknesses": "",
            "strengths": ""
        }

        Write guidelines:
        """

        guidelines_fuse_model = OpenAIModel(
            api_key=self.api_key, 
            model='gpt-3.5-turbo',
            response_format = { "type": "json_object" }
            )
        print("Guidelines last run:", self.guidelines_last_run['json_guidelines']['weaknesses'],
        self.guidelines_last_run['json_guidelines']['strengths'])

        guidelines_fuse_model.set_system_prompt(SYSTEM_FREE_RECALL_GENERATE_GUIDELINES_PROMPT.format(
            #rewritten_document=rewritten_document,
            weaknesses_guidelines=self.guidelines_last_run['json_guidelines']['weaknesses'],
            strengths_guidelines=self.guidelines_last_run['json_guidelines']['strengths'],
            agent_1_feedback="""
            """,
            agent_2_feedback="""
            """
        ))

        #convert string to json
        
        guidelines_response = guidelines_fuse_model.run(self.feedback_document)
        self.step_num += 1

        try: 
            self.guidelines = json.loads(guidelines_response)
        except json.JSONDecodeError as e:
            self.guidelines = {"weaknesses": "Try to get your best!", "strengths": ""}
            print(f"Error decoding guidelines: {e}")

        return self.guidelines

    def push_guidelines(self) -> None:
        """
        Push the user's document to the API for processing.
        """
        
        #VALIDATE GUIDELINES
        
        #GENERATE NUMBER TEMP
        import random
        random_number = random.randint(1000, 9999)

        #BUILD JSON
        #GET RECENT GUIDELINES
        #UPDATE
        #PUSH GUIDELINES

        import datetime

        current_time = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        iso_timestamp =  datetime.datetime.strptime(current_time.isoformat(), "%Y-%m-%dT%H:%M:%S%z").timestamp()  # Adding 'Z' to indicate UTC time

        self._put_item_to_dynamodb(
            table_name=self.table_name,
            item={
                'UserId_TopicId_TS': self.user_topic_key,
                'GSI_ISO': int(iso_timestamp),
                'json_guidelines': self.guidelines,
                'user_draft': 
                    {
                    'raw':self.rewritten_document,
                    'rewritten':self.rewritten_document,
                    },
                'user_id': self.user_id,
                'topic': self.topic,
            }
        )
        print(f"Guidelines pushed to DynamoDB: {self.guidelines}")


    def retrieve_documents(self, topics: List[str]) -> List[str]:
        """
        Retrieve documents related to the specified topics from the database or API.
        """
        # Possible implementation details
        pass

    def process_free_recall_draft(self, draft: str) -> Dict[str, Any]:
        """
        Process the user's free recall draft and generate feedback and recommendations.
        """
        # Steps to clean the draft, call the LLM API, analyze feedback, etc.
        pass

    @staticmethod
    def _put_item_to_dynamodb(table_name, item):
        """
        """
        # Create a DynamoDB service client
        dynamodb = boto3.resource('dynamodb')

        # Access the specified table
        table = dynamodb.Table(table_name)

        try:
            # Put the item into the table
            response = table.put_item(Item=item)
            return response

        except Exception as e:
            print(f"Error putting item into DynamoDB: {e}")
            return None


    @staticmethod
    def _get_latest_user_topic_data(table_name, user_topic_key):
        """
        Fetch the latest item for a given user_id and topic_id from a DynamoDB table,
        using a GSI to order by the timestamp.

        :param table_name: Name of the DynamoDB table
        :param user_id: User ID to filter the data
        :param topic_id: Topic ID to further filter the data
        :param gsi_name: Name of the Global Secondary Index for ordering by GSI_ISO
        :return: The most recent item based on GSI_ISO for the specified user_id and topic_id
        """
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        try:
            response = table.query(
                KeyConditionExpression=Key('UserId_TopicId_TS').eq(user_topic_key),
                ScanIndexForward=False,  # Sorts the results in descending order based on GSI_ISO
                Limit=1  # Retrieves only the most recent item
            )

            items = response.get('Items', [])
            if not items:
                print(f"No items found for user_topic_key: {user_topic_key}")
                return None

            return items[0]

        except Exception as e:
            print(f"Error fetching item from DynamoDB: {e}")
            return None
