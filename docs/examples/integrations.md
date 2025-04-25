# Custom Integrations

This page demonstrates ways to integrate nGPT into larger applications and systems, showing how it can be embedded in various real-world scenarios.

## Web Application Integration

### Flask Web Application

Here's an example of integrating nGPT into a Flask web application:

```python
from flask import Flask, request, jsonify, render_template
from ngpt import NGPTClient, load_config
import os

app = Flask(__name__)

# Initialize the client
config = load_config()
client = NGPTClient(**config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        response = client.chat(prompt, stream=False)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/code', methods=['POST'])
def generate_code():
    data = request.json
    prompt = data.get('prompt', '')
    language = data.get('language', 'python')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        code = client.generate_code(prompt, language=language)
        return jsonify({'code': code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

The corresponding basic HTML template (`templates/index.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>nGPT Web Interface</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { margin-top: 20px; }
        #response { white-space: pre-wrap; background: #f1f1f1; padding: 15px; border-radius: 5px; }
        textarea { width: 100%; height: 100px; margin-bottom: 10px; }
        button { padding: 8px 16px; background: #4CAF50; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>nGPT Web Interface</h1>
    
    <div class="chat-container">
        <h2>Chat with AI</h2>
        <textarea id="prompt" placeholder="Enter your message here..."></textarea>
        <button onclick="sendChat()">Send</button>
        <h3>Response:</h3>
        <div id="response"></div>
    </div>
    
    <script>
        async function sendChat() {
            const prompt = document.getElementById('prompt').value;
            const responseElement = document.getElementById('response');
            
            if (!prompt) return;
            
            responseElement.textContent = "Loading...";
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt }),
                });
                
                const data = await response.json();
                
                if (data.error) {
                    responseElement.textContent = `Error: ${data.error}`;
                } else {
                    responseElement.textContent = data.response;
                }
            } catch (error) {
                responseElement.textContent = `Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

## Command-Line Tool Integration

### Building a Custom Research Assistant

Create a specialized command-line tool for research assistance:

```python
#!/usr/bin/env python3
# research_assistant.py

import argparse
import sys
import os
import json
from datetime import datetime
from ngpt import NGPTClient, load_config
from ngpt.cli.formatters import COLORS

def save_to_research_db(topic, query, response):
    """Save research results to a JSON database file."""
    db_file = os.path.expanduser("~/research_results.json")
    
    # Load existing data
    if os.path.exists(db_file):
        with open(db_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    # Add new entry
    data.append({
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "query": query,
        "response": response
    })
    
    # Save data
    with open(db_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return db_file

def main():
    parser = argparse.ArgumentParser(description="Research Assistant powered by nGPT")
    parser.add_argument("query", nargs="?", help="Research query")
    parser.add_argument("-t", "--topic", default="general", help="Research topic/category")
    parser.add_argument("-f", "--file", help="Read query from file")
    parser.add_argument("-o", "--output", help="Save results to specified file")
    parser.add_argument("-w", "--web-search", action="store_true", help="Enable web search for current information")
    parser.add_argument("-d", "--depth", type=int, choices=[1, 2, 3], default=2, 
                        help="Research depth (1=basic, 2=detailed, 3=comprehensive)")
    
    args = parser.parse_args()
    
    # Get query from file or command line
    if args.file:
        try:
            with open(args.file, 'r') as f:
                query = f.read().strip()
        except Exception as e:
            print(f"{COLORS['yellow']}Error reading file: {e}{COLORS['reset']}", file=sys.stderr)
            return 1
    elif args.query:
        query = args.query
    else:
        parser.print_help()
        return 1
    
    # Configure depth to system prompt
    depth_prompts = {
        1: "Provide a brief overview with key points only.",
        2: "Provide a detailed explanation with examples.",
        3: "Provide a comprehensive analysis with multiple perspectives, examples, and references."
    }
    
    system_prompt = f"""You are a research assistant helping with information on {args.topic}.
{depth_prompts[args.depth]}
Organize your response with clear headings and bullet points where appropriate."""
    
    # Initialize nGPT client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"{COLORS['yellow']}Error initializing nGPT client: {e}{COLORS['reset']}", file=sys.stderr)
        return 1
    
    # Prepare messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    
    print(f"Researching: {query}")
    print(f"Topic: {args.topic}")
    print(f"Depth: {args.depth}")
    print("Please wait...")
    
    try:
        # Get response
        response = client.chat("", messages=messages, web_search=args.web_search)
        
        # Output handling
        if args.output:
            with open(args.output, 'w') as f:
                f.write(response)
            print(f"\n{COLORS['green']}Research results saved to: {args.output}{COLORS['reset']}")
        else:
            print("\n" + "=" * 50)
            print(response)
            print("=" * 50)
        
        # Save to research database
        db_file = save_to_research_db(args.topic, query, response)
        print(f"{COLORS['green']}Results also saved to research database: {db_file}{COLORS['reset']}")
        
        return 0
    except Exception as e:
        print(f"{COLORS['yellow']}Error: {e}{COLORS['reset']}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Usage:

```bash
# Make the script executable
chmod +x research_assistant.py

# Basic research query
./research_assistant.py "How do solar panels work?"

# With a specific topic and web search
./research_assistant.py "Latest advancements in quantum computing" -t "Physics" -w

# Comprehensive research saved to file
./research_assistant.py "Impact of climate change on agriculture" -d 3 -o climate_research.txt
```

## Integration with Task Automation

### GitHub Issue Summarizer

Create a tool that summarizes GitHub issues and generates suggested responses:

```python
#!/usr/bin/env python3
# github_issue_helper.py

import argparse
import sys
import requests
from ngpt import NGPTClient, load_config
from ngpt.cli.formatters import COLORS

def fetch_github_issue(repo, issue_number, token=None):
    """Fetch issue details from GitHub API."""
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    issue = response.json()
    
    # Also fetch comments
    comments_url = issue["comments_url"]
    comments_response = requests.get(comments_url, headers=headers)
    comments_response.raise_for_status()
    comments = comments_response.json()
    
    return issue, comments

def summarize_issue(client, issue, comments):
    """Use nGPT to summarize the issue and comments."""
    issue_body = issue["body"] or ""
    issue_title = issue["title"]
    
    # Format comments
    comments_text = ""
    for i, comment in enumerate(comments):
        comments_text += f"\nComment {i+1} by {comment['user']['login']}:\n{comment['body']}\n"
    
    # Prepare prompt
    prompt = f"""GitHub Issue Title: {issue_title}
    
Issue Description:
{issue_body}

{comments_text}

Please analyze this GitHub issue and provide:
1. A concise summary of the issue
2. Key points mentioned in the discussion
3. Any questions that need answering
4. A suggested response or next steps
"""
    
    system_prompt = "You are a helpful GitHub issue assistant. Analyze issues and provide concise summaries and suggested responses."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    return client.chat("", messages=messages)

def main():
    parser = argparse.ArgumentParser(description="GitHub Issue Helper powered by nGPT")
    parser.add_argument("repo", help="GitHub repository in format 'owner/repo'")
    parser.add_argument("issue", type=int, help="Issue number")
    parser.add_argument("-t", "--token", help="GitHub API token (for private repos or higher rate limits)")
    parser.add_argument("-o", "--output", help="Save results to specified file")
    
    args = parser.parse_args()
    
    try:
        # Initialize nGPT client
        config = load_config()
        client = NGPTClient(**config)
        
        # Fetch issue details
        print(f"Fetching issue #{args.issue} from {args.repo}...")
        issue, comments = fetch_github_issue(args.repo, args.issue, args.token)
        
        # Summarize issue
        print("Analyzing issue...")
        summary = summarize_issue(client, issue, comments)
        
        # Output handling
        if args.output:
            with open(args.output, 'w') as f:
                f.write(summary)
            print(f"{COLORS['green']}Analysis saved to: {args.output}{COLORS['reset']}")
        else:
            print("\n" + "=" * 50)
            print(summary)
            print("=" * 50)
        
        return 0
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"{COLORS['yellow']}Error: Issue #{args.issue} not found in repository {args.repo}{COLORS['reset']}", file=sys.stderr)
        elif e.response.status_code == 401:
            print(f"{COLORS['yellow']}Error: Authentication failed. Check your GitHub token{COLORS['reset']}", file=sys.stderr)
        else:
            print(f"{COLORS['yellow']}HTTP Error: {e}{COLORS['reset']}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"{COLORS['yellow']}Error: {e}{COLORS['reset']}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Usage:

```bash
# Make the script executable
chmod +x github_issue_helper.py

# Analyze a public GitHub issue
./github_issue_helper.py "nazdridoy/ngpt" 42

# With GitHub token for private repos
./github_issue_helper.py "nazdridoy/ngpt" 42 -t your_github_token

# Save analysis to file
./github_issue_helper.py "nazdridoy/ngpt" 42 -o issue_analysis.txt
```

## Integration with Desktop Applications

### PyQt Text Editor with AI Assistance

Create a simple text editor with AI capabilities using PyQt5:

```python
#!/usr/bin/env python3
# ai_text_editor.py

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox,
                            QInputDialog, QMessageBox, QSplitter, QMenu, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.code import code_mode

class AIAssistThread(QThread):
    """Thread for non-blocking AI operations."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, client, operation, text, **kwargs):
        super().__init__()
        self.client = client
        self.operation = operation
        self.text = text
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "generate":
                response = self.client.chat(self.text, stream=False, **self.kwargs)
            elif self.operation == "improve":
                prompt = f"Please improve the following text for clarity and style:\n\n{self.text}"
                response = self.client.chat(prompt, stream=False, **self.kwargs)
            elif self.operation == "summarize":
                prompt = f"Please summarize the following text:\n\n{self.text}"
                response = self.client.chat(prompt, stream=False, **self.kwargs)
            elif self.operation == "code":
                response = self.client.generate_code(self.text, language=self.kwargs.get("language", "python"))
            else:
                response = "Unknown operation"
            
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

class AITextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_client()
    
    def init_client(self):
        """Initialize the nGPT client."""
        try:
            config = load_config()
            self.client = NGPTClient(**config)
            self.statusBar().showMessage("nGPT client initialized successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize nGPT client: {str(e)}")
            self.client = None
    
    def init_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("AI-Enhanced Text Editor")
        self.setGeometry(100, 100, 1000, 600)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Editor area
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Type or paste text here...")
        editor_layout.addWidget(self.editor)
        
        # Editor controls
        editor_controls = QHBoxLayout()
        
        self.improve_btn = QPushButton("Improve")
        self.improve_btn.clicked.connect(self.improve_text)
        editor_controls.addWidget(self.improve_btn)
        
        self.summarize_btn = QPushButton("Summarize")
        self.summarize_btn.clicked.connect(self.summarize_text)
        editor_controls.addWidget(self.summarize_btn)
        
        self.generate_btn = QPushButton("Generate from Prompt")
        self.generate_btn.clicked.connect(self.generate_from_prompt)
        editor_controls.addWidget(self.generate_btn)
        
        editor_layout.addLayout(editor_controls)
        
        # Assistant area
        assistant_widget = QWidget()
        assistant_layout = QVBoxLayout(assistant_widget)
        
        assistant_layout.addWidget(QLabel("AI Assistant Output"))
        
        self.assistant_output = QTextEdit()
        self.assistant_output.setReadOnly(True)
        assistant_layout.addWidget(self.assistant_output)
        
        # Assistant controls
        assistant_controls = QHBoxLayout()
        
        self.code_btn = QPushButton("Generate Code")
        self.code_btn.clicked.connect(self.generate_code)
        assistant_controls.addWidget(self.code_btn)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["python", "javascript", "html", "css", "java", "c++", "rust", "go"])
        assistant_controls.addWidget(self.language_combo)
        
        self.clear_output_btn = QPushButton("Clear Output")
        self.clear_output_btn.clicked.connect(self.assistant_output.clear)
        assistant_controls.addWidget(self.clear_output_btn)
        
        assistant_layout.addLayout(assistant_controls)
        
        # Add widgets to splitter
        splitter.addWidget(editor_widget)
        splitter.addWidget(assistant_widget)
        splitter.setSizes([500, 500])
        
        # Set splitter as central widget
        self.setCentralWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Create menus
        self.create_menus()
    
    def create_menus(self):
        """Create application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.editor.clear)
        file_menu.addAction(new_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        insert_action = QAction("Insert AI Output", self)
        insert_action.triggered.connect(self.insert_ai_output)
        edit_menu.addAction(insert_action)
        
        # AI menu
        ai_menu = menubar.addMenu("AI")
        
        temperature_action = QAction("Set Temperature", self)
        temperature_action.triggered.connect(self.set_temperature)
        ai_menu.addAction(temperature_action)
        
        model_action = QAction("Change Model", self)
        model_action.triggered.connect(self.change_model)
        ai_menu.addAction(model_action)
        
        # Set default values
        self.temperature = 0.7
        self.model = None  # Use default from config
    
    def improve_text(self):
        """Improve the current text for clarity and style."""
        text = self.editor.toPlainText()
        if not text:
            self.statusBar().showMessage("No text to improve", 3000)
            return
        
        self.statusBar().showMessage("Improving text...")
        self.assistant_output.setPlainText("Working on improving your text...")
        
        # Create a thread for non-blocking operation
        self.thread = AIAssistThread(
            self.client, "improve", text, 
            temperature=self.temperature
        )
        self.thread.finished.connect(self.handle_ai_response)
        self.thread.error.connect(self.handle_ai_error)
        self.thread.start()
    
    def summarize_text(self):
        """Summarize the current text."""
        text = self.editor.toPlainText()
        if not text:
            self.statusBar().showMessage("No text to summarize", 3000)
            return
        
        self.statusBar().showMessage("Summarizing text...")
        self.assistant_output.setPlainText("Working on summarizing your text...")
        
        # Create a thread for non-blocking operation
        self.thread = AIAssistThread(
            self.client, "summarize", text, 
            temperature=self.temperature
        )
        self.thread.finished.connect(self.handle_ai_response)
        self.thread.error.connect(self.handle_ai_error)
        self.thread.start()
    
    def generate_from_prompt(self):
        """Generate content from a prompt."""
        prompt, ok = QInputDialog.getMultiLineText(
            self, "Enter Prompt", "What would you like the AI to generate?", ""
        )
        
        if not ok or not prompt:
            return
        
        self.statusBar().showMessage("Generating content...")
        self.assistant_output.setPlainText("Working on generating content...")
        
        # Create a thread for non-blocking operation
        self.thread = AIAssistThread(
            self.client, "generate", prompt, 
            temperature=self.temperature
        )
        self.thread.finished.connect(self.handle_ai_response)
        self.thread.error.connect(self.handle_ai_error)
        self.thread.start()
    
    def generate_code(self):
        """Generate code from description."""
        description = self.editor.toPlainText()
        if not description:
            self.statusBar().showMessage("No description for code generation", 3000)
            return
        
        language = self.language_combo.currentText()
        self.statusBar().showMessage(f"Generating {language} code...")
        self.assistant_output.setPlainText(f"Working on generating {language} code...")
        
        # Create a thread for non-blocking operation
        self.thread = AIAssistThread(
            self.client, "code", description, 
            language=language
        )
        self.thread.finished.connect(self.handle_ai_response)
        self.thread.error.connect(self.handle_ai_error)
        self.thread.start()
    
    def handle_ai_response(self, response):
        """Handle the AI response."""
        self.assistant_output.setPlainText(response)
        self.statusBar().showMessage("Done", 3000)
    
    def handle_ai_error(self, error_message):
        """Handle AI errors."""
        QMessageBox.warning(self, "AI Error", f"Error: {error_message}")
        self.assistant_output.setPlainText(f"Error: {error_message}")
        self.statusBar().showMessage("Error occurred", 3000)
    
    def insert_ai_output(self):
        """Insert AI output into the editor."""
        output = self.assistant_output.toPlainText()
        if output:
            cursor = self.editor.textCursor()
            cursor.insertText(output)
    
    def set_temperature(self):
        """Set the temperature parameter for AI responses."""
        temp, ok = QInputDialog.getDouble(
            self, "Set Temperature", 
            "Enter temperature (0.0-1.0):", 
            self.temperature, 0.0, 1.0, 2
        )
        
        if ok:
            self.temperature = temp
            self.statusBar().showMessage(f"Temperature set to {temp}", 3000)
    
    def change_model(self):
        """Change the AI model."""
        model, ok = QInputDialog.getText(
            self, "Change Model", 
            "Enter model name (leave empty for default):", 
            text=self.model or ""
        )
        
        if ok:
            self.model = model if model else None
            if self.model:
                self.statusBar().showMessage(f"Model changed to {model}", 3000)
            else:
                self.statusBar().showMessage("Using default model", 3000)

def main():
    app = QApplication(sys.argv)
    window = AITextEditor()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

To run the AI text editor:

```bash
# Install required dependencies
pip install PyQt5

# Run the editor
python ai_text_editor.py
```

## Next Steps

These examples demonstrate how to integrate nGPT into various applications and workflows. You can adapt and extend these examples to fit your specific needs.

For more information on the nGPT API, refer to the [API Reference](../api/README.md). 