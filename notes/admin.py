from django.contrib import admin
from .models import Note


# Register your modals here.

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'created_at', 'updated_at', 'user')
