import os
import base64
import numpy as np
import json
import re
from openai import AsyncOpenAI  
from anthropic import AsyncAnthropic 
from prompts import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# Instantiate async clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Helper function to parse the combined response
def parse_api_response(response_text: str):
    """
    Parses the API response string to separate HTML content and JSON metadata.
    Expects JSON in a code block formatted like: ```json { ... } ```
    """
    html_content = response_text
    metadata = {}

    # Regex to find any JSON block inside triple backticks
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL | re.IGNORECASE)

    if json_match:
        json_string = json_match.group(1)
        try:
            metadata = json.loads(json_string)
            # Remove the matched block from the HTML content
            html_content = response_text[:json_match.start()].strip() + "\n" + response_text[json_match.end():].strip()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON metadata: {e}")
            metadata = {"error": "Failed to parse JSON"}
    
    # Basic cleanup for leftover markers
    # html_content = re.sub(r'```json\s*', '', html_content, flags=re.IGNORECASE).strip()
    # html_content = re.sub(r'\s*```', '', html_content).strip()
    html_match = re.search(r'```(?:html)?\s*(.*?)\s*```', html_content, re.DOTALL | re.IGNORECASE)
    if html_match:
        html_content = html_match.group(1).strip()

    return {"html": html_content, "metadata": metadata}


async def call_async_api(provider: str, input_data: str, is_image: bool = False) -> dict:
    """
    Unified ASYNCHRONOUS API call for both OpenAI and Anthropic providers.

    Args:
        provider (str): The provider to use ('openai' or 'anthropic').
        input_data (str): The text input or base64 image data.
        is_image (bool): True if the input_data represents an image.

    Returns:
        dict: A dictionary containing 'html' and 'metadata'.
               Returns {'error': 'message'} if an API call fails.
    """
    global SYSTEM_PROMPT
    rand_val = np.random.rand(1)[0]
    formatted_system_prompt = SYSTEM_PROMPT.format(rand_val)

    try:
        if provider.lower() == 'openai':
            if is_image:
                messages = [
                    {'role': 'system', 'content': formatted_system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{input_data}"}} # Assuming PNG, adjust if needed
                        ]
                    }
                ]
            else:
                 messages = [
                    {'role': 'system', 'content': """Generate a similar math question based on the user's text. Font should be black. Provide only the HTML/LaTeX for the question and the JSON metadata block as specified. Format: HTML code followed by ```json #metadata { ... } ```"""},
                    {"role": "user", "content": input_data}
                 ]

            response = await openai_client.chat.completions.create( 
                model="gpt-4o", 
                messages=messages,
                temperature=0.5 
            )
            raw_response = response.choices[0].message.content
            return parse_api_response(raw_response)

        elif provider.lower() == 'anthropic':
            if is_image:
                 messages=[
                     {
                         "role": "user",
                         "content": [
                             {
                                 "type": "image",
                                 "source": {
                                     "type": "base64",
                                     "media_type": "image/png", # Assuming PNG
                                     "data": input_data,
                                 },
                             },
                             {"type": "text", "text": "Apply the following instructions:"}
                         ]
                     }
                 ]
                 system = formatted_system_prompt

            else:
                messages=[{"role": "user", "content": input_data}]
                system = """Generate a similar math question based on the user's text. Provide only the HTML/LaTeX for the question and the JSON metadata block as specified. Format: HTML code followed by ```json #metadata { ... } ```"""

            message = await anthropic_client.messages.create( 
                model="claude-3-5-sonnet-latest", 
                max_tokens=3000, 
                messages=messages,
                system=system,
                temperature=0.7 
            )
            raw_response = message.content[0].text
            print(raw_response)
            return parse_api_response(raw_response)
        else:
            raise ValueError("Unsupported provider. Please choose either 'openai' or 'anthropic'.")

    except Exception as e:
        print(f"API Error ({provider}): {str(e)}")
        return {"error": f"{provider.capitalize()} API Error: {str(e)}"}
    
