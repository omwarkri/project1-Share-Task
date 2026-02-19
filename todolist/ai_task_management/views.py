import openai
from chat.models import ChatAIMessage
from google import generativeai  # Note the capital 'C' in Client
client =  generativeai.configure(api_key="AIzaSyAlvIwjLl9S5tr3IQa3RtZf0Li7i8wXHXg")
model=generativeai.GenerativeModel('gemini-2.5-flash')

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
from task.models import Task, SubTask
import re

genai.configure(api_key="AIzaSyAEm8U3DW756WMqX_6OLDAHQNnYIY9SFjY")

@require_GET
@csrf_exempt
def ai_subtask_suggestions(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Prompt focused on quality and engagement without emojis
    prompt = f"""Generate creative subtasks for: "{task.title}".
    Requirements:
    1. Make each subtask genuinely engaging and not boring
    2. Focus on quality over quantity - suggest only valuable steps
    3. No emojis or special characters
    4. Use action-oriented language
    5. Include variety in approach types
    6. Make them feel rewarding to complete
    
    Good examples:
    "Turn this into a 10-minute challenge against the clock"
    "Research three surprising facts about this topic"
    "Create a visual representation of your progress"
    "Teach what you learn to someone else"
    "Identify the most enjoyable aspect and amplify it"
    
    Generate the best subtasks you can think of (don't number them):
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        response_data = []
        created_count = 0
        
        for line in raw_lines:
            # Clean the line thoroughly
            clean_line = re.sub(r"^\s*\d+[.)]\s*", "", line)  # Remove numbering
            clean_line = re.sub(r"^[-•*]\s*", "", clean_line)  # Remove bullets
            clean_line = clean_line.replace('"', '').strip()
            
            if clean_line and len(clean_line.split()) >= 3:  # Ensure meaningful content
                subtask = SubTask.objects.create(
                    task=task,
                    title=clean_line,
                    completed=False
                )
                response_data.append({
                    "id": subtask.id,
                    "title": subtask.title
                })
                created_count += 1
                
                # Limit to a reasonable number of quality subtasks
                if created_count >= 8:
                    break

        return JsonResponse({
            "success": True, 
            "subtasks": response_data,
            "message": f"Created {created_count} engaging steps for your task!",
            "quality_check": "Each subtask designed to maintain interest"
        })

    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "message": "Failed to generate engaging subtasks"
        }, status=500)







from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from task.models import Task,  SubTask 
from .models import Microtask
from django.views.decorators.http import require_http_methods
import json


def microtask_page(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, "microtasks.html", {"task": task})

def get_microtasks(request, task_id):
    microtasks = Microtask.objects.filter(task_id=task_id).values("id", "title", "completed")
    return JsonResponse(list(microtasks), safe=False)

@csrf_exempt
def add_microtask(request, task_id):
    data = json.loads(request.body)
    title = data.get("title", "")
    if title:
        Microtask.objects.create(task_id=task_id, title=title)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Title required"}, status=400)

@csrf_exempt
def toggle_microtask(request, microtask_id):
    microtask = get_object_or_404(Microtask, id=microtask_id)
    microtask.completed = not microtask.completed
    microtask.save()
    return JsonResponse({"status": "ok"})

@csrf_exempt
def delete_microtask(request, microtask_id):
    microtask = get_object_or_404(Microtask, id=microtask_id)
    microtask.delete()
    return JsonResponse({"status": "deleted"})

@csrf_exempt
def update_microtask(request, microtask_id):
    data = json.loads(request.body)
    title = data.get("title", "")
    if not title:
        return JsonResponse({"error": "Title required"}, status=400)
    microtask = get_object_or_404(Microtask, id=microtask_id)
    microtask.title = title
    microtask.save()
    return JsonResponse({"status": "updated"})

from chat.models import ChatAIMessage
from .models import Microtask
from task.models import Task, SubTask
from google import generativeai
from django.http import JsonResponse

from google import generativeai
from django.http import JsonResponse
from .models import Task, Microtask  # Ensure these are imported
from google import generativeai
from django.http import JsonResponse
from .models import Task, Microtask  # Ensure these are imported

# Configure the generative AI model
generativeai.configure(api_key="AIzaSyAlvIwjLl9S5tr3IQa3RtZf0Li7i8wXHXg")
model = generativeai.GenerativeModel('gemini-2.5-flash')


from django.http import JsonResponse
from .models import Task, SubTask, Microtask
import google.generativeai as generativeai

# Configure the generative AI model
generativeai.configure(api_key="AIzaSyAlvIwjLl9S5tr3IQa3RtZf0Li7i8wXHXg")
model = generativeai.GenerativeModel('gemini-2.5-flash')

def generate_microtasks_for_each_subtask(request, subtask_id):
    """
    Generate entertaining microtasks for each subtask of a given task using AI
    """
    try:
        subtask = SubTask.objects.select_related('task').get(id=subtask_id)
        task = Task.objects.prefetch_related('subtasks').get(id=subtask.task_id)

        subtasks = task.subtasks.all()
        all_microtasks = {}

        for sub in subtasks:
            prompt = f"""
            I have a task titled: "{task.title}".
            One of its subtasks is: "{sub.title}".

            Please generate 3-5 fun and entertaining microtasks specifically for this subtask.
            Make them engaging and enjoyable to complete.
            Return only the microtasks in a bullet point list without any asterisks or other special characters at the beginning.
            """

            try:
                response = model.generate_content(prompt)
                raw_text = response.text.strip()

                # Clean up the response - remove any *, -, • or other bullet point markers
                microtask_list = [
                    line.strip().lstrip('*-• ').strip()
                    for line in raw_text.split("\n")
                    if line.strip()
                ]

                created_microtasks = []
                for title in microtask_list:
                    microtask = Microtask.objects.create(
                        task=task,
                        subtask=sub,
                        title=title,
                        is_entertaining=True  # Assuming you have this field
                    )
                    created_microtasks.append(title)

                all_microtasks[sub.title] = created_microtasks

            except Exception as e:
                all_microtasks[sub.title] = [f"Error generating microtasks: {str(e)}"]
                continue

        return JsonResponse({
            'status': 'success',
            'generated_microtasks': all_microtasks,
            'message': 'Fun microtasks generated successfully!'
        })

    except SubTask.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': f'SubTask with id {subtask_id} does not exist'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)



from django.http import JsonResponse

from django.http import JsonResponse
from .models import Microtask  # Adjust if your model import path differs
import google.generativeai as generativeai

generativeai.configure(api_key="AIzaSyAlvIwjLl9S5tr3IQa3RtZf0Li7i8wXHXg")
model = generativeai.GenerativeModel('gemini-2.5-flash')

def get_microtask_instructions(request, microtask_id):
    try:
        microtask = Microtask.objects.select_related('subtask', 'task').get(id=microtask_id)
        task_title = microtask.task.title
        subtask_title = microtask.subtask.title
        microtask_title = microtask.title

        prompt = f"""
        I am working on a task titled: "{task_title}".
        One of its subtasks is: "{subtask_title}".
        I need to complete the following microtask: "{microtask_title}".

        Please provide a clear, step-by-step list of instructions (3 to 7 steps) that would help someone execute this microtask effectively.
        Each step should be practical and actionable. Do not return anything other than the steps.
        """

        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        instructions = [
            line.strip("- ").strip()
            for line in raw_text.split("\n")
            if line.strip()
        ]

        return JsonResponse({'instructions': instructions})

    except Microtask.DoesNotExist:
        return JsonResponse({
            'error': 'Microtask not found.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

