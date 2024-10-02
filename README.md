# socratic-chatbot-genai-hackathon
 The Socratic Chatbot Assistant was created for the Gen AI Exchange Hackathon, powered by Google Gen AI. This chatbot helps users explore and understand data structures and algorithms by engaging them in a Socratic-style conversation, encouraging deeper learning through thoughtful questioning. Using technologies like Django, HTML, CSS, and JavaScript, the chatbot leverages Google Gen AI to provide smart, context-aware responses. It's designed to be a valuable learning tool for both students and educators in computer science.

# Socratic Chatbot Assistant

The Socratic Chatbot Assistant is designed to help users explore and understand data structures and algorithms through engaging Socratic-style conversations. This project was developed for the Gen AI Exchange Hackathon powered by Google Gen AI.

## Installation

Follow these steps to set up the project locally:

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Clone the Repository

```bash
git clone https://github.com/your-username/socratic-chatbot-genai-hackathon.git
cd socratic-chatbot-genai-hackathon
```

### Setup a Virtual Environment

```bash 
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

```

### Install Dependencies
Install the required packages using the requirements.txt file:

```bash
pip install -r requirements.txt
```
### Update the Google API Key 

In the views.py file, replace the placeholder for the Google API key with your actual API key:
```bash
# views.py
GOOGLE_API_KEY = 'YOUR_GOOGLE_API_KEY'
```

### Migrate the database
Run the following command to apply database migrations:

```bash
python manage.py migrate
```

### Run the Django Development Server
```bash
python manage.py runserver
```

