import base64
import os
from dotenv import load_dotenv
import os
from openai import OpenAI
from agno.models.openai import OpenAIChat
from agno.models.anthropic.claude import Claude
from agno.agent import Agent
from agno.media import Image
from prompts import eval_prompt

from playwright.sync_api import sync_playwright

load_dotenv()
openai_client = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"), id='gpt-4o-mini')
anthropic_client = Claude(api_key=os.getenv("ANTHROPIC_API_KEY"), id='claude-3-5-sonnet-latest') #'claude-sonnet-4-20250514')#


def render_and_eval_html(html: str, provider: str) -> str:
    """
    1. Renders `html` in headless Chromium.
    2. Takes a full-page screenshot.
    3. Embeds the screenshot as a base64 data-URL in a Markdown image tag.
    4. Sends the Eval Prompt plus:
       - A code-fence containing the HTML
       - The embedded screenshot
    5. Returns GPT's raw response as a string.
    """
    
     # taking screenshot of image. 
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        png_bytes = page.screenshot(full_page=True)
        browser.close()

     # --- encode screenshot to data URL ---
    b64 = base64.b64encode(png_bytes).decode("ascii")   

    if provider.lower() == 'o':
        client_model = openai_client
        input_date_string = f"data:image/png;base64,{b64}"
    else:
        client_model = anthropic_client
        input_date_string = b64

    math_generator = Agent(model = client_model,
                           instructions=eval_prompt,
                        #    reasoning=True
                            expected_output='''Your output MUST follow this order:
                                                ---
                                                1. The corrected HTML code inside ```html<html> ... ``` tags.
                                                2. The metadata wrapped in ```json ... ``` tags, preceded by `#metadata`.
                                                3. An explanation of changes you made, in 3 clear steps (even if the change is just validation or confirmation).
                                                ---
                                            '''
                           )
    
    if provider.lower() == 'o':
        res = math_generator.run('analyze',images=[Image(url=input_date_string)])
    else:
        image_bytes = base64.b64decode(input_date_string)
        res = math_generator.run('analyze',images=[Image(content=image_bytes)])

    return res.content


if __name__ == "__main__":
    sample_html = """
<html>
<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.min.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="p-6">
<div class="max-w-2xl mx-auto">
<p class="text-gray-700 mb-4">The figure is made of two rectangular prisms.</p>
<svg class="mb-6" height="200" viewbox="0 0 300 200" width="300">
<!-- Bottom prism -->
<path d="M 50,150 L 250,150 L 250,100 L 200,70 L 50,70 Z" fill="none" stroke="black"></path>
<line stroke="black" x1="250" x2="250" y1="100" y2="150"></line>
<!-- Top prism -->
<path d="M 100,70 L 160,70 L 160,30 L 100,30 Z" fill="none" stroke="black"></path>
<line stroke="black" x1="160" x2="160" y1="30" y2="70"></line>
<!-- Dimensions -->
<text class="text-sm" x="30" y="110">4 in.</text>
<text class="text-sm" x="140" y="170">10 in.</text>
<text class="text-sm" x="260" y="125">6 in.</text>
<text class="text-sm" x="120" y="65">4 in.</text>
<text class="text-sm" x="165" y="50">3 in.</text>
<text class="text-sm" x="130" y="25">2 in.</text>
</svg>
<p class="text-gray-700 mb-6">Which is the volume of the figure?</p>
<div class="space-y-3">
<div class="p-3 border rounded-lg hover:bg-gray-50">
<label class="flex items-center space-x-3">
<input name="answer" type="radio" value="216"/>
<span>216 cubic inches</span>
</label>
</div>
<div class="p-3 border rounded-lg hover:bg-gray-50">
<label class="flex items-center space-x-3">
<input name="answer" type="radio" value="264"/>
<span>264 cubic inches</span>
</label>
</div>
<div class="p-3 border rounded-lg hover:bg-gray-50 bg-green-50">
<label class="flex items-center space-x-3">
<input checked="" name="answer" type="radio" value="252"/>
<span>252 cubic inches</span>
</label>
</div>
<div class="p-3 border rounded-lg hover:bg-gray-50">
<label class="flex items-center space-x-3">
<input name="answer" type="radio" value="288"/>
<span>288 cubic inches</span>
</label>
</div>
</div>
</div>
</body>
</html>
    """
    result = render_and_eval_html(sample_html)
    print(result)