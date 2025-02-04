from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status','category']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label_suffix = " *" if field.required else ""




# forms.py
from django import forms
from .models import Comment,SubTask

class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Only the 'text' field is needed for the form
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Add a comment...', 
                'class': 'form-control'
            }),
        }   
class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ['title', 'completed'] 
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter subtask title...',
                'class': 'form-control',
            }),
        }
