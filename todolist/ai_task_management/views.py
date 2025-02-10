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

    # Save AI response in the database
    ChatAIMessage.objects.create(task_id=task_id, sender="AI", message=ai_response)

    return ai_response



    

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from task.models import Task
from chat.models import ChatAIMessage
from task.forms import TaskNotesForm

@csrf_exempt
def chat_ai_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    messages = ChatAIMessage.objects.filter(task_id=task_id).order_by('timestamp')
    notes_form=TaskNotesForm()
    if request.method == 'POST':
        user_message = request.POST.get('user_message')
        print(user_message)
        
        # Save user message to database
        if user_message:
            ChatAIMessage.objects.create(task_id=task_id, sender="User", message=user_message)

            # Mock AI Response
            ai_response = generate_ai_response(task_id,user_message)
            print(ai_response)
            ChatAIMessage.objects.create(task_id=task_id, sender="AI", message=ai_response)

        return redirect('ai_task_management', task_id=task.id)
    for message in messages:
        print(message)
    return render(request, 'ai_task_management.html', {'task': task, 'procedure': task.procedure, 'messages': messages,'notes_form':notes_form})


