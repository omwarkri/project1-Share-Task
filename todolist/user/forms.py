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

from django import forms
from task.models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'status', 'is_daily']  # 👈 no `is_active`
        widgets = {
            'title': forms.TextInput(attrs={'id': 'title-input'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)  # You can remove this line if unused
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_active = True  # 👈 force is_active to True silently
        if commit:
            instance.save()
        return instance


      