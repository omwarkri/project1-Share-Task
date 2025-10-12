import google.generativeai as genai
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task
import json

# Configure Gemini API
genai.configure(api_key="AIzaSyAlvIwjLl9S5tr3IQa3RtZf0Li7i8wXHXg")
model = genai.GenerativeModel('gemini-2.5-flash')

@login_required
def get_ai_posts(request):
    user = request.user
    tasks = Task.objects.filter(user=user).order_by("-created_at")[:10]
    task_titles = [task.title for task in tasks]

    prompt = f"""
    User has recently planned or completed these tasks: {task_titles}.

    Generate **20 unique insights** based on these tasks. Each insight should be a complete post with a mix of and informative for user and encouraging motivating:
    - A short story 
    - Facts 
    - A productivity thought 
    - Practical knowledge 
    - Motivational elements 
    - Actionable tips 
    - Scientific/psychological facts 

    ### Response Format:
    Return a **valid JSON array** inside markdown triple backticks like this:
    ```
    [
        {{"post": "Your first post here..." }},
        {{"post": "Your second post here..." }},
        ...
        {{"post": "Your twentieth post here..." }}
    ]
    ```
    Ensure the response **only** contains the JSON inside backticks.
    """

    try:
        response = model.generate_content(prompt)
        ai_text = response.candidates[0].content.parts[0].text.strip()
        json_text = ai_text.split("```")[1].strip()
        posts = json.loads(json_text)
    except (IndexError, json.JSONDecodeError, KeyError):
        posts = [{"post": "AI response is not valid JSON format. Please try again."}]

    return JsonResponse({"posts": posts})

@login_required
def get_ai_memes(request):
    user = request.user
    tasks = Task.objects.filter(user=user).order_by("-created_at")[:10]
    task_titles = [task.title for task in tasks]

    prompt = f"""
    User has recently planned or completed these tasks: {task_titles}.
    
    Generate **10 funny meme captions** based on these tasks. Captions should be:
    - Witty and humorous
    - Relatable to productivity, motivation, or daily struggles
    - Short (1-2 lines max)

    **Return ONLY a valid JSON array. No markdown. No explanations. Just JSON.**
    Example:
    [
        {{"meme_text": "When you finish a task and realize there's more waiting..." }},
        {{"meme_text": "That feeling when you check off a task but forget to save your progress..." }},
        {{"meme_text": "When the deadline is tomorrow, and