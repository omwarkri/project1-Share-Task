from django import forms
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'profile_picture']



from django import forms

class UserInterestGoalForm(forms.Form):
    interests = forms.CharField(widget=forms.Textarea, help_text="Enter your interests, separated by commas.")
    goals = forms.CharField(widget=forms.Textarea, help_text="Enter your goals, separated by commas.")

from task.models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'status', 'is_daily']
        widgets = {
            'title': forms.TextInput(attrs={'id': 'title-input'}),  # ✅ Set an ID for JS
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the current user from kwargs
        super().__init__(*args, **kwargs)

      