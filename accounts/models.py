from django.db import models
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=64)
    email = forms.EmailField(max_length=64)

    class Meta(UserCreationForm.Meta):
        models = User
        fields = UserCreationForm.Meta.fields + ('name', 'email',)

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.user_name = self.cleaned_data['name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user

