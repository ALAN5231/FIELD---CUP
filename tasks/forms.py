from django.forms import ModelForm
from django import forms
from .models import Task, Team, Tournament

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']
        
class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'image']