from abc import ABC, abstractmethod
from typing import Any, Dict

import openai
import tiktoken

def prompt_cost(model_type: str, num_prompt_tokens: float, num_completion_tokens: float):
    input_cost_map = {
        "gpt-3.5-turbo": 0.0015,
        "gpt-3.5-turbo-16k": 0.003,
        "gpt-3.5-turbo-0613": 0.0015,
        "gpt-3.5-turbo-16k-0613": 0.003,
        "gpt-4": 0.03,
        "gpt-4-0613": 0.03,
        "gpt-4-32k": 0.06,
        "gpt-4-1106-preview": 0.01,
        "gpt-4-1106-vision-preview": 0.01,
    }

    output_cost_map = {
        "gpt-3.5-turbo": 0.002,
        "gpt-3.5-turbo-16k": 0.004,
        "gpt-3.5-turbo-0613": 0.002,
        "gpt-3.5-turbo-16k-0613": 0.004,
        "gpt-4": 0.06,
        "gpt-4-0613": 0.06,
        "gpt-4-32k": 0.12,
        "gpt-4-1106-preview": 0.03,
        "gpt-4-1106-vision-preview": 0.03,
    }

    if model_type not in input_cost_map or model_type not in output_cost_map:
        return -1

    return num_prompt_tokens * input_cost_map[model_type] / 1000.0 + num_completion_tokens * output_cost_map[model_type] / 1000.0


class OpenAIModel():

    def __init__(self, api_key: str, model: str, response_format = None):
        """
        ...
        response_format = { "type": "json_object" }
        """
        self.model = model
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.client = openai.OpenAI(api_key=api_key)
        self.provider = 'openai'
        self.response_format = response_format

        self.model_config_dict = {
            "temperature": 0.0,
        }

        self.num_max_token_map = {
                    "gpt-3.5-turbo": 4096,
                    "gpt-3.5-turbo-16k": 16384,
                    "gpt-3.5-turbo-0613": 4096,
                    "gpt-3.5-turbo-16k-0613": 16384,
                    "gpt-4": 8192,
                    "gpt-4-0613": 8192,
                    "gpt-4-32k": 32768,
                    "gpt-4-1106-preview": 4096,
                    "gpt-4-1106-vision-preview": 4096,
                }
        
        self.model_config_dict.update({
            "max_tokens": self.num_max_token_map[self.model]
        })

    def run(self, user_content: str):
        """
        user_content: str
        """

        num_content_tokens = len(self.encoding.encode(user_content))

        if isinstance(self.system_prompt, str):

            messages = [
                {
                    "role":"system",
                    "content": self.system_prompt
                },
                {
                    "role":"user",
                    "content": user_content
                }
            ]

            num_prompt_tokens = len(self.encoding.encode(self.system_prompt))

            print(f"Number of tokens system: {num_prompt_tokens}")
            print(f"Number of tokens user's file-content: {num_content_tokens}")
            print(f"Total input tokens: {num_prompt_tokens + num_content_tokens}")

            num_max_completion_tokens = 4096 #= self.model_config_dict['max_tokens'] - num_prompt_tokens - num_content_tokens

        else:

            messages = [
                {
                    "role":"user",
                    "content": user_content
                }
            ]

            num_max_completion_tokens = 4096 #self.num_max_token_map[self.model] - num_content_tokens
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.model_config_dict['temperature'],
            max_tokens=num_max_completion_tokens,
            response_format=self.response_format
            )
        
        print(f"Number of tokens output: {len(self.encoding.encode(response.choices[0].message.content))}")
        
        return response.choices[0].message.content

    def set_system_prompt(self, system_prompt: str):
        self.system_prompt = system_prompt
