import os
import google.generativeai as genai
from django.shortcuts import render, redirect
from Chatbot.models import UserRegistration
from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gtts import gTTS
import io
import pygame
import os
import base64
import threading
from langdetect import detect
import tempfile
from django.contrib.auth.decorators import login_required
import mimetypes
from PyPDF2 import PdfReader
from PIL import Image
from io import BytesIO

os.environ['GOOGLE_API_KEY'] = "GOOGLE_API_KEY"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


# Define the prompt for Socratic chatbot
system_instruction = """You are a multilingual and insightful Socratic teacher and guide, dedicated to encouraging
        users to learn independently by asking the most thought-provoking and relevant questions upto some point until they understand.
        As a teaching assistant specializing in Data Structures and Algorithms, you understand
        complex queries and guide the learning journey by consistently posing the best possible
        questions with examples that stimulate critical thinking and self-discovery."""
prompt = """
<Persona>
    You are a multilingual, helpful Socratic teacher and guide, aiming to push users to learn independently by asking insightful and thought-provoking questions. Students can come from any background and want to explore Data Structures and Algorithms.
</Persona>
 
<Task>
    Socratic Teaching Assistant for Data Structures and Algorithms
</Task>
 
<Context>
    You comprehend questions about Data Structures and Algorithms and respond with relevant guiding questions. Accept input in text, images, audio, video, or PDF formats. Maintain continuity by referencing previous interactions and checking the user's understanding before moving on.
</Context>
 
<Tone>
    Polite and Technical
</Tone>
 
<Examples>
<Example>
<User role="user">
<Question>What is bubble sorting?</Question>
</User>
<Assistant role="model">
<Response>Let's start with the basics: How would you describe what sorting means? What do you think happens to adjacent elements during bubble sort?</Response>
</Assistant>
</Example>
<Example>
<User role="user">
<Question>I don't get how bubble sort works.</Question>
</User>
<Assistant role="model">
<Response>That's okay! Can you explain what you find confusing about it? What do you think is the first step in sorting elements using bubble sort?</Response>
</Assistant>
</Example>
<Example>
<User role="user">
<InputType>Image</InputType>
<Description>A diagram of bubble sort.</Description>
</User>
<Assistant role="model">
<Response>Looking at this diagram, can you identify what happens during each pass? What do you think the diagram is trying to convey about the swapping process?</Response>
</Assistant>
</Example>
<Example>
<User role="user">
<Question>Can you explain merge sort?</Question>
</User>
<Assistant role="model">
<Response>Before we dive into merge sort, let's recap what you've learned about sorting so far. What do you feel confident about, and what aspects would you like to clarify further?</Response>
</Assistant>
</Example>
</Examples>
 
<Instructions>
<Step number="1">
        Analyze the user's input to categorize it as a greeting, general question, or DSA-related question.
</Step>
<Step number="2">
        Respond Accordingly:
<SubStep number="1">
            For greetings: Acknowledge politely but keep it brief.
</SubStep>
<SubStep number="2">
            For DSA questions:
<Action>
                    Check for the user's understanding first. If they express confusion, ask clarifying questions to help them articulate their thoughts. Avoid providing answers; instead, guide them toward a better understanding.
</Action>
</SubStep>
<SubStep number="3">
            For unrelated topics: Politely inform the user of your focus on Data Structures and Algorithms.
</SubStep>
</Step>
<Step number="3">
        Continuously check the user's understanding, using their responses to gauge when to introduce new topics or questions.
</Step>
<Step number="4">
        If the user demonstrates understanding, prompt them with questions about related concepts to explore next.
</Step>
<Step number="5">
        Adapt responses based on user input, avoiding repetition while referencing earlier points in the conversation.
</Step>
</Instructions>
"""
language_code_map = {
    'hi': 'hi',    # Hindi
    'ta': 'ta',    # Tamil
    'bn': 'bn',    # Bengali
    'te': 'te',    # Telugu
    'kn': 'kn',    # Kannada
    'ml': 'ml',    # Malayalam
    'mr': 'mr',    # Marathi
    'gu': 'gu',    # Gujarati
    'pa': 'pa',    # Punjabi
    'ur': 'ur',    # Urdu
}


# Define generation configuration
generation_config = {
    "temperature": 0.5,
    "top_p": 0.9,
    "top_k": 40,
    "num_beams": 5,
    "no_repeat_ngram_size": 2,
    "repetition_penalty": 2,
    "response_mime_type": "text/plain",
    "convert_system_message_to_human": True
}


# Initialize the Generative Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)
def index(request):
    return render(request,'index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')


        try:
            user = UserRegistration.objects.get(email=email)
            if user.password == password:
                request.session['fullname'] = user.username
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
        except UserRegistration.DoesNotExist:
            messages.error(request, 'User does not exist.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        fullname = request.POST['fullname']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if UserRegistration.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('register')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        new_user = UserRegistration.objects.create(
            username = fullname,
            email=email,
            password=password
        )
        messages.success(request, 'Registration successful. You can now log in.')
        return redirect('login')


    return render(request, 'register.html')


def home(request):
    fullname = request.session.get('fullname')
    return render(request,'home.html',{'fullname':fullname})


def play_audio_from_text(text, language_code):
    try:
        tts = gTTS(text=text, lang=language_code, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            audio_file = temp_file.name  
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)  
        pygame.mixer.music.play()


        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        os.remove(audio_file)


    except Exception as e:
        print(f"Error in generating audio: {e}")


def generate_output(user_input):
    content = [user_input, prompt]
    response = model.generate_content(
        content,
        generation_config=generation_config
    )
    return response.text
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        user_input = request.POST.get('message')
        attachment = request.FILES.get('attachment')

        # Check if both message and attachment are missing
        if not user_input and not attachment:
            return JsonResponse({"error": "No message or attachment provided"}, status=400)

        # If an attachment is provided, determine the file type
        if attachment:
            file_type = mimetypes.guess_type(attachment.name)[0]

            # Process PDF file
            if file_type == 'application/pdf':
                pdf_reader = PdfReader(attachment)
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text()
                user_input += " [PDF Content]: " + pdf_text

            # Process Image file
            elif file_type.startswith('image'):
                try:
                    # Open the image and convert it to base64
                    image = Image.open(attachment)
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")  # Convert image to PNG or keep the original format
                    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                    # Append base64 string to the user input or process it further
                    user_input += f" [Image provided (Base64)]: {img_base64}"

                except Exception as e:
                    return JsonResponse({"error": f"Image processing failed: {str(e)}"}, status=500)

            # Unsupported file type
            else:
                return JsonResponse({"error": "Unsupported file type"}, status=400)
        try:
            response = generate_output(user_input)
            detected_lang = detect(response)
            language_code = language_code_map.get(detected_lang, 'en')
            threading.Thread(target=play_audio_from_text, args=(response, language_code)).start()
            
            return JsonResponse({"response": response}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)