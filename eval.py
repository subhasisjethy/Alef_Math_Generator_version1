import base64
import os
from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()
# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url='http://localhost:1234/v1')
from playwright.sync_api import sync_playwright
# openai_client = OpenAI(api_key='lm', base_url='http://localhost:1234/v1')
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def render_and_eval_html(html: str, model: str = "gpt-4.1-mini") -> str:
    """
    1. Renders `html` in headless Chromium.
    2. Takes a full-page screenshot.
    3. Embeds the screenshot as a base64 data-URL in a Markdown image tag.
    4. Sends the SYSTEM_PROMPT plus:
       - A code-fence containing the HTML
       - The embedded screenshot
    5. Returns GPT's raw response as a string.
    """

    eval_prompt = """
    You will receive two inputs:
    1. The HTML code of a previously generated math question.
    2. An image file showing its rendered output.

    Your critical tasks — DO NOT SKIP ANY:
    ---
    0. Check if the question contains terms such as *volume*, *cube*, *3D*, or any concept that inherently requires a 3D diagram. If so, replace or upgrade any existing 2D diagrams to a **true 3D rendering** using **SVG**. Ensure the diagram is interactive or visually represents 3D (e.g., isometric view, axes depth).
    1. Compare the HTML rendering and the provided image: ensure that the **layout**, **text**, **math symbols**, and **diagrams** are perfectly consistent.
    2. For any SVG diagram, check for **mathematical correctness**. Recreate it if needed to accurately reflect the math in the question.
    3. If it's a multiple-choice question, confirm that:
    - All options are shown.
    - The correct answer is present.
    - **No answer is visually marked as selected**.
    4. **Always regenerate the HTML code**, even if no changes seem needed, to maintain consistency and validation.
    5. Then, generate metadata in JSON format with only these keys:
    - **grade**
    - **topic**
    - **learning_objective**
    - **difficulty**
    - **question_type**
    - **correct_answer**

    ### Output Format:
    Your output MUST follow this order:
    ---
    1. The corrected HTML code inside ```html ... ``` tags.
    2. The metadata wrapped in ```json ... ``` tags, preceded by `#metadata`.
    3. An explanation of changes you made, in 3 clear steps (even if the change is just validation or confirmation).

    ---

    Instruction: Always explain the changes or validations made in three clear steps. If you detected no visible changes in the diagram, still rewrite the HTML to confirm and explain why no diagram changes were needed.

    """
    # --- render & screenshot in memory ---
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        png_bytes = page.screenshot(full_page=True)
        browser.close()

    # --- encode screenshot to data URL ---
    b64 = base64.b64encode(png_bytes).decode("ascii")
    # image_md = f"![rendered output](data:image/png;base64,{b64})"
    # --- build the chat messages ---
    messages = [
        {'role': 'system', 'content': eval_prompt},
        {
            "role": "user",
            "content": [
                { "type": "text", "text": f"{html}" },
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        }
    ]

    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {str(e)}"



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
    result = render_html_and_query_chatgpt(sample_html)
    print(result)