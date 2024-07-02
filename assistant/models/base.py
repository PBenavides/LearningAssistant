"""
As far we can map that LLMs calls can be:

1.- Regular calls with specific objectives (system prompts)
2.- Retrieval calls that can use more information within the context.
3.- Action calls: That will act and use some tool (can be retrieval tool)

"""
import os
from openai import OpenAI
import tiktoken
import logging

logging.basicConfig(level=logging.INFO)

api_key = os.environ['OPENAI_API_KEY']
encoding = tiktoken.get_encoding("cl100k_base")

def chat_completion(
    messages: list,
    model='gpt-3.5-turbo',
    temperature=0,
    max_tokens=None,
    response_format=None
):
    """
    messages: [
        {
      "role": "user",
      "content": ""
    },
    ]
    """
    client = OpenAI(
    api_key=api_key
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format
    )
    return response

def regular_straight_call(
    system_prompt: str,
    user_content: str,
    model='gpt-3.5-turbo',
    temperature=0,
    max_tokens=2000,
    response_format=None
):

    messages = [
        {
            "role":"system",
            "content": system_prompt
        },
        {
            "role":"user",
            "content": user_content
        }
    ]

    num_tokens_system = len(encoding.encode(messages[0]["content"]))
    num_tokens_user = len(encoding.encode(messages[1]["content"]))

    logging.info(f"Number of tokens system: {num_tokens_system}")
    logging.info(f"Number of tokens user's file-content: {num_tokens_user}")
    logging.info(f"Total input tokens: {num_tokens_system + num_tokens_user}")
    logging.info("-----------------------------------------------"*3)

    response = chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format
    )

    num_output_tokens = len(encoding.encode(response.choices[0].message.content))

    logging.info(f"Number of tokens output: {num_output_tokens}")

    return response.choices[0].message.content


import os
from functools import partial
import litellm
import instructor
from litellm import token_counter
from litellm import completion as litellm_completion
from litellm.exceptions import (
    APIConnectionError,
    RateLimitError,
    ServiceUnavailableError,
)

from dotenv import load_dotenv
load_dotenv()

#Tmp
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LanguageModel:
    """
    A class for interacting with any LLM AI Language Model API.
    This can be configured to work with structured outputs.

    Attributes:
        model_name (str): The name of the model to use.
        api_key (str): The API key to use.
        base_url (str): The base URL to use if required.
        api_version (str): The API version to use.
        num_retries (int): The number of retries to use.
        llm_timeout (int): The timeout to use.
        temperature (float): The temperature to use.
        llm_top_p (float): The top-p to use.
        response_format (object): For LLM's you will have { "type": "json_object" }
        structured_output (bool): Whether to use structured output.
        output_schema_response (object): The output schema response to use in Pydantic.
    """

    def __init__(
            self,
            model_name=None,
            api_key=None,
            base_url=None,
            api_version=None,
            num_retries=None,
            llm_timeout=None,
            temperature=None,
            llm_top_p=None,
            response_format=None
    ):

        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.api_version = api_version
        self.num_retries = num_retries
        self.llm_timeout = llm_timeout
        self.temperature = temperature
        self.llm_top_p = llm_top_p
        self.response_format = response_format
        
        self.message_history = []

        #litellms has all the required information to interact with the model.
        try:
            self.model_info = litellm.get_model_info(model=self.model_name)
        except:
            logging.error(f"Failed to get model info for {self.model_name}")

        self._completion = partial(
            self._log_and_store_completion,
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            api_version=self.api_version,
            num_retries=self.num_retries,
        )

        litellm.set_verbose=False # 👈 this is the 1-line change you need to make

        self.total_current_cost = 0

    def _log_and_store_completion(self, messages: list,
                                  structured_output=None,
                                  response_model=None,
                                  **kwargs):
        """
        A method to log, store and execute messages sent to the completion endpoint.
        """
        
        self.structured_output = structured_output
        
        # Filtering kwargs to remove None values and unsupported parameters
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}

        self.message_history.append(messages)

        print('Printing filtered kwargs', filtered_kwargs)

        # Perform the API call
        if structured_output is not None and response_model is not None:
            
            print('We are going through instructor')
            self.response_model = response_model
            #add it into kwargs

            client = instructor.from_litellm(litellm_completion)

            response = client.chat.completions.create(
                messages=messages,
                max_retries=3,
                response_model=response_model,
                **filtered_kwargs
            )

        else:
            response = litellm_completion(messages=messages, **filtered_kwargs)

        # Log the response
        logging.info(f"Model response for {self.model_name}: {response.choices[0].message.content}")

        return response

    @property
    def completion(self):
        return self._completion
    
    def get_token_costs(self, messages, type='input'):
        """
        Get the number of tokens in a list of messages.

        Args:
            messages (list): A list of messages.

        Returns:
            int: The number of tokens.
        """

        total_tokens = litellm.token_counter(model=self.model_name, messages=messages)
        if type == 'input': 
            total_token_cost = total_tokens * self.model_info['input_cost_per_token']
        else:
            total_token_cost = total_tokens * self.model_info['output_cost_per_token']

        return total_token_cost

    def __str__(self):
        """
        Return a human-readable string representation of the LanguageModel instance.
        """
        return (f"LanguageModel(model_name={self.model_name}, base_url={self.base_url}, "
                f"api_version={self.api_version}, num_retries={self.num_retries}, "
                f"timeout={self.llm_timeout}, temperature={self.temperature}, "
                f"top_p={self.llm_top_p})", f"response_format={self.response_format}")