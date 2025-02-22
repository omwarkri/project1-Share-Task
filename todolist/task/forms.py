from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'status', 'dependencies']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),  # Use HTML5 date input
        }
    dependencies = forms.ModelMultipleChoiceField(
        queryset=Task.objects.all(), 
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

class TaskDependenciesForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['dependencies']

    dependencies = forms.ModelMultipleChoiceField(
        queryset=Task.objects.all(), 
        widget=forms.CheckboxSelectMultiple,
        required=False
    )




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



# forms.py
from django import forms
from notes_app.models import TaskNotes

class TaskNotesForm(forms.ModelForm):
    class Meta:
        model = TaskNotes
        fields = ['note_text']
        widgets = {
            'note_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add a note...'}),
        }