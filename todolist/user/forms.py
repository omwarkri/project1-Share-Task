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
