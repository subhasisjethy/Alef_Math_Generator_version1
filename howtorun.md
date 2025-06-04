# 🧠 Question Generator Web App

A simple Flask web app that generates questions based on provided image and text.

## 📦 Directory Structure
```
templates/
  index.html
api.py
app.py
prompts.py
requirements.txt
```

## 🚀 How to Run

1. **Navigate to the project:**
   ```bash
   cd <your-project-folder>
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   ```
   http://localhost:5000
   ```

## 🛠 Change API Provider

To switch between AI providers (`anthropic` or `openai`), edit this line in `app.py`:

```python
api_provider = 'anthropic'  # Change to 'openai' if needed
```
------

## Optional - Repomix file contains all code inside Markdown
```repomix-output.md``` can be used as cursor rule if needed in cursor.
