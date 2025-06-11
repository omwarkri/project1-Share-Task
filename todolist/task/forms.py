from django import forms
from .models import Task


from django import forms
from django.utils import timezone
from .models import Task

from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'status', 'dependencies', 'is_daily']
        widgets = {
            'title': forms.TextInput(attrs={'id': 'title-input'}),  # ✅ Set an ID for JS
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the current user from kwargs
        super().__init__(*args, **kwargs)

        # ✅ Set dependencies field dynamically
        self.fields['dependencies'] = forms.ModelMultipleChoiceField(
            queryset=Task.objects.filter(user=user) if user else Task.objects.none(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
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

from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Only the 'text' field is needed for the form
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Add a comment...',
                'rows': 3,
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




from django import forms
from .models import Team
from user.models import CustomUser

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description']



class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Select User")

class TaskForm(forms.ModelForm):
    dependencies = forms.ModelMultipleChoiceField(
        queryset=Task.objects.none(),  # Start with an empty queryset
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'status', 'dependencies', 'is_daily']
        widgets = {
            'title': forms.TextInput(attrs={}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get user from kwargs
        super().__init__(*args, **kwargs)

        # Only show the user's tasks as dependency options
        if user:
            self.fields['dependencies'].queryset = Task.objects.filter(user=user)






class TeamTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'status', 'assigned_to' ]
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),  # Use HTML5 datetime input
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the current user from kwargs
        super().__init__(*args, **kwargs)

        # Filter dependencies to only include tasks for the current user
        if user:
            self.fields['dependencies'].queryset = Task.objects.filter(user=user)

    dependencies = forms.ModelMultipleChoiceField(
        queryset=Task.objects.none(),  # Start with an empty queryset
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )





from django import forms
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()

class ReassignTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['assigned_to','status']

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            # Limit the assignee choices to team members
            self.fields['assigned_to'].queryset = team.members.all()


class EscalateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['escalation_reason']
        widgets = {
            'escalation_reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter the reason for escalation...'}),
        }
        labels = {
            'escalation_reason': 'Reason for Escalation',
        }


from django import forms
from .models import Appreciation

class AppreciationForm(forms.ModelForm):
    class Meta:
        model = Appreciation
        fields = ['to_user', 'message']