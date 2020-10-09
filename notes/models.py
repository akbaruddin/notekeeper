from django.db import models
from django import forms

from django.core.signing import Signer
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt
from taggit.managers import TaggableManager
# Create your models here.


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=200)
    note_content = encrypt(models.TextField(null=True, blank=True))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=200, unique=True)
    tags = TaggableManager()
    signer = Signer(salt='notes.Note')


class AddNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = '__all__'
        exclude = ['slug', 'user']
        widgets = {
            'tags': forms.TextInput(
                attrs={
                    'data-role': 'tagsinput',
                }
            )
        }
