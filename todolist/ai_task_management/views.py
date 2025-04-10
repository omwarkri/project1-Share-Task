import openai
from chat.models import ChatAIMessage
from google import generativeai  # Note the capital 'C' in Client
client =  generativeai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")
model=generativeai.GenerativeModel('gemini-1.5-flash')

def generate_ai_response(task_id, user_message):
    # Fetch recent chat history for context (limit to last N messages if needed)
    chat_history = ChatAIMessage.objects.filter(task_id=task_id).order_by('-timestamp')[:10][::-1]


    # Format conversation history for the AI model
    conversation = [
        {"role": "system", "content": "You are an AI assistant."}
    ]
    
    for message in chat_history:
        role = "user" if message.sender == "User" else "assistant"
        conversation.append({"role": role, "content": message.message})

    # Add the user's latest message
    conversation.append({"role": "user", "content": user_message})

    prompt = f"Provide a step-by-step procedure to accomplish the task '{conversation}"

    response = model.generate_content(
        prompt
    )

    # Extract AI response text
    ai_response = response.text
    

    return ai_response



    
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from task.models import Task
from notes_app.models import TaskNotes  # Assuming you have a Note model related to the task
from chat.models import ChatAIMessage
from notes_app.forms import TaskNoteForm

@csrf_exempt
def ai_taskmanagement_view(request, task_id):
    print("ai task manegement")
    task = get_object_or_404(Task, id=task_id)
    print(task.id,"these is task id")
    messages = ChatAIMessage.objects.filter(task_id=task_id).order_by('timestamp')
    notes_form = TaskNoteForm()

    # Fetch all notes associated with this task
    notes = TaskNotes.objects.filter(task=task)  # Assuming your notes are related to the task

    if request.method == 'POST':
        user_message = request.POST.get('user_message')
        print(user_message)
        
        # Save user message to database
        if user_message:
            ChatAIMessage.objects.create(task_id=task_id, sender="User", message=user_message)

            # Mock AI Response
            ai_response = generate_ai_response(task_id, user_message)
            print(ai_response)
            ChatAIMessage.objects.create(task_id=task_id, sender="AI", message=ai_response)

        return redirect('ai_task_management', task_id=task.id)

    # For debugging: print all messages
    for message in messages:
        print(message)


   

    # Render the template and pass the notes as well
    return render(request, 'ai_task_management.html', {
        'task': task,
        'procedure': task.procedure,
        'messages': messages,
        'notes': notes,  # Pass notes to the template
        'notes_form': notes_form
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Add this import
from django.shortcuts import get_object_or_404
from task.models import Task
# from chat.models import ChatAIMessage
import json

@csrf_exempt
def chat_ai_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        # Parse the JSON data from the request
        data = json.loads(request.body)
        user_message = data.get('user_message')

        if user_message:
            # Save user message to the database
            ChatAIMessage.objects.create(task_id=task_id, sender="User", message=user_message)

            # Generate AI response
            ai_response = generate_ai_response(task_id, user_message)

            # Save AI response to the database
            ChatAIMessage.objects.create(task_id=task_id, sender="AI", message=ai_response)

            # Return the AI response as JSON
            return JsonResponse({
                'status': 'success',
                'ai_response': ai_response
            })

    elif request.method == 'GET':
        # Fetch all messages for the task
        messages = ChatAIMessage.objects.filter(task_id=task_id).order_by('timestamp')
        messages_list = [
            {
                'sender': message.sender,
                'message': message.message,
                'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for message in messages
        ]
        return JsonResponse(messages_list, safe=False)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from task.models import Task
import re
genai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")

@require_GET
@csrf_exempt
def ai_subtask_suggestions(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"Generate 4 helpful subtasks for the main task: \"{task.title}\". Keep them short and actionable."
    
    response = model.generate_content(prompt)

    # Parse response safely (you can adjust this based on the format Gemini returns)
    text = response.text.strip()
    suggestions = []

    for line in text.splitlines():
        # Clean line: remove bullets, asterisks, and sequence numbers like "1.", "1)", etc.
        clean_line = re.sub(r"^\s*(?:[-•*]|\d+[.)])\s*", "", line)  # remove bullets or numbering
        clean_line = clean_line.replace("**", "").strip()  # remove bold markers
        if clean_line:
            suggestions.append(clean_line)

    return JsonResponse(suggestions, safe=False)
