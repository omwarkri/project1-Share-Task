from django import forms
from .models import TaskNotes

class TaskNoteForm(forms.ModelForm):
    class Meta:
        model = TaskNotes
        fields = ['note_text']
        widgets = {
            'note_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your note here...'}),
        }
