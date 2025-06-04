# api.py
"""
Module for Agno interactions.
Handles calls to the ChatGPT & Claude API.
"""

from prompts import SYSTEM_PROMPT, eval_prompt
import numpy as np
import streamlit as st
from agno.models.openai import OpenAIChat, OpenAILike
from agno.models.anthropic.claude import Claude
from agno.agent import Agent
from agno.media import Image
import base64
from dotenv import load_dotenv
import os
from eval_run import render_and_eval_html
import json 
import re
from bs4 import BeautifulSoup


load_dotenv()

# Instantiate clients for each provider.
# Adjust the OpenAI client instantiation as needed for your OpenAI library version.
openai_client = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"), id='gpt-4o-mini') #, reasoning_effort='low')
# openai_client = OpenAILike(api_key='lm', id='o4-mini', base_url='http://localhost:1234/v1')
anthropic_client = Claude(api_key=os.getenv("ANTHROPIC_API_KEY"), id='claude-3-7-sonnet-latest')# id= 'claude-sonnet-4-20250514') #id='claude-3-5-sonnet-latest') #'claude-sonnet-4-20250514')#


def extract_html_from_string(text):
    """
    Extracts a syntactically valid HTML snippet from a string that may contain
    both text and HTML code. Returns cleaned HTML suitable for use with
    st.container_html() in Streamlit.
    """

    # Look for HTML tags (including <html>, <div>, <body>, etc.)
    html_snippet_match = re.search(r'(<html[\s\S]*?</html>|<body[\s\S]*?</body>|<div[\s\S]*?</div>)', text, re.IGNORECASE)

    if not html_snippet_match:
        # Fallback: Try to detect any generic HTML tag in the text
        tag_match = re.search(r'<[a-z][\s\S]*?>', text, re.IGNORECASE)
        if not tag_match:
            return None  # No HTML found at all

        # Try to extract everything from the first tag onward
        start_index = tag_match.start()
        html_candidate = text[start_index:]
    else:
        html_candidate = html_snippet_match.group()

    # Clean and validate HTML using BeautifulSoup
    soup = BeautifulSoup(html_candidate, "html.parser")
    cleaned_html = str(soup)

    return cleaned_html

def extract_json_from_string(text):
    """
    Finds the first ```json … ``` block in `text`, 
    then captures from its opening “{” to the matching final “}” 
    (so inner “{…}” in strings won’t confuse it), and returns
    the parsed JSON object (or None if there was no valid JSON).
    """
    import json
    pattern = re.compile(
        r"```json[\s\S]*?(\{[\s\S]*\})[\s\S]*?```",
        re.DOTALL
    )
    match = pattern.search(text)
    if not match:
        return None

    json_str = match.group(1)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None  

def parse_api_response(response_text: str):
    """
    Parses the API response string to separate HTML content and JSON metadata.
    Expects JSON in a code block formatted like: ```json { ... } ```
    """
    html_content = response_text
    metadata = {}


    try:
        metadata = extract_json_from_string(html_content)
        # Remove the matched block from the HTML content
        html_string = extract_html_from_string(html_content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON metadata: {e}")
        metadata = {"error": "Failed to parse JSON"}
    

    return {"html": html_string, "metadata": metadata} 


def call_async_api(provider: str, input_data: str, is_image: bool = False) -> str:
    from textwrap import dedent
    global SYSTEM_PROMPT
    rand_val = np.random.rand(1)[0]
    SYSTEM_PROMPT = SYSTEM_PROMPT.format(rand_val)

    if provider.lower() == 'o':
        client_model = openai_client
        input_date_string = f"data:image/png;base64,{input_data}"
    else:
        client_model = anthropic_client
        input_date_string = input_data
    math_generator = Agent(model = client_model,
                           description="You are smart system designed designed to similar but not same question - you will not skip instructions provided - Do not approach to solve question, be remember what user asks in instruction",
                           instructions=SYSTEM_PROMPT,
                           expected_output= dedent('''Output Format:
                                                    ```html
                                                    <!-- your regenerated question HTML here -->
                                                    ```

                                                    ```json
                                                    #metadata
                                                    {
                                                    "grade": "...",
                                                    "topic": "...",
                                                    "learning_objective": "...",
                                                    "difficulty": "...",
                                                    "question_type": "...",
                                                    "correct_answer": "..."
                                                    }
                                                    ```''')
                        #    reasoning=True
                           )
    
    if is_image and provider.lower() == 'o':
        res = math_generator.run('analyze',images=[Image(url=input_date_string)])
    elif is_image and provider.lower() == 'a':
        image_bytes = base64.b64decode(input_date_string)
        res = math_generator.run('analyze',images=[Image(content=image_bytes)])
    else:
        res = math_generator.run(input_data)

    # out = render_and_eval_html(res.content, provider=provider)
    print(res.content)
    # print(out)
    return parse_api_response(res.content)


if __name__=='__main__':
    print(call_async_api('o', "generate similar math question"))
