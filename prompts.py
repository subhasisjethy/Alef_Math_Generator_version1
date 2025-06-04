# prompts.py
"""
This module contains prompt strings used by the API module.
Add or modify prompts here.
"""


SYSTEM_PROMPT = """Generate similar question (interactive) But not same question in same layout with distinct values and diagram (RESET QUESTION NOs IF THERE).  And Provide metadata. 

<hide>
Make sure metadata should contains correct answer. To make sure correct, you solve question first and add correct answer in metadata.
Do not display answer on question html
</hide>

<key>
Instruction: html component should be interactive. 
DO NOT ATTEMPT TO SOLVE QUESTION: 
DO NOT PROVIDE SUBMIT BUTTON
Use svg for diagram and use text-anchor to highlight labels.
</key>

if 'diagram' in image:
   Generate interactive question with html, svg, mathjax & latex, svg (cdnjs)
   **Make sure diagram is mathematically correct**

else: 
   Generate question with html & latex

For variation think of seed from 0 to 1: if 0 means least variation and 1 means most variation from original question. 

variation: {}

Use tailwind css to design. Make sure fonts on svg appropriate only 1 or 2 unit bigger than question.

LaTeX Support:

If LaTeX is present, include MathJax by adding <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.min.js"></script> in the <head>.

Wrap inline math in ... and block math in:

```html
<div>
  \[
    ...math content...
  \]
</div>
```

DO NOT PROVIDE EXPLAINATION ONLY CODE BEFORE AND AFTER CODE
output html code: 
"""

eval_prompt = """You will receive two inputs:
1. The HTML code of the question you previously generated.
2. An image file showing its rendered output.

Your task:
0: Question seems like require 3D image then make sure it should be 3D, using SVG.
1. Compare the HTML and the image to ensure they match exactly in layout, values, and diagram. Add labels if required for diagram.
2. Verify any SVG diagram is mathematically accurate and reflects the question requirements.
3. If it’s a multiple-choice question, check that all options are present and the correct answer is included but not highlighted.
4. Remove any highlights or selections from the correct answer.
5. Regenerate the HTML code so it precisely matches the validated image.
6. Produce metadata for the question in JSON with these keys only: **grade**, **topic**, **learning_objective**, **difficulty**, **question_type**, **correct_answer**.

Output rules:
- DO NOT PROVIDE EXPLANATION BEFORE OR AFTER CODE.
- First emit the corrected HTML code by itself. Code should be wrapped inside <html> tag
- Then emit the metadata JSON wrapped in triple backticks, preceded by `#metadata`.

Output Format:

```html
<html>
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
```
An explanation of changes you made, in 3 clear steps (even if the change is just validation or confirmation).
"""


bkp_prompt = """Generate similar question in same layout with distinct values and diagram (RESET QUESTION NOs IF THERE).


if 'diagram' in image:
   Generate question with html, d3, svg, mathjax & latex (cdnjs)
   **Make sure diagram is mathematically correct**

else: 
   Generate question with html & latex

For variation think of seed from 0 to 1: if 0 means least variation and 1 means most variation from original question. 

variation: {}

Use tailwind css to design. Make sure fonts on svg appropriate only 1 or 2 unit bigger than question.

LaTeX Support:

If LaTeX is present, include MathJax by adding <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.min.js"></script> in the <head>.

Wrap inline math in ... and block math in:

```html
<div>
  \[
    ...math content...
  \]
</div>
```

if html: 
   - DO NOT PROVIDE EXPLAINATION BEFORE AND AFTER CODE
   - Provide metadata of question wrapped inside json with keys: **grade**, **topic**, **learning_objective**, **difficulty**, **question_type**, **correct_answer** only.
     Output Format:
     ```json
     #metadata  here
     ```
"""