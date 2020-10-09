from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Note, AddNoteForm


# Create your views here.
@login_required
def home(request):
    if request.user.is_authenticated:
        notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
        all_notes = Note.objects.filter(user=request.user).order_by('-updated_at')

        if request.method == 'POST':
            form = AddNoteForm(request.POST)
            if form.is_valid():
                form_data = form.save(commit=False)
                form_data.user = request.user
                form_data.save()

                form.save_m2m()
                form = AddNoteForm()
                messages.success(request, 'Note added successfully!')
                return redirect('notes')
        else:
            form = AddNoteForm()

        context = {
            'notes': notes,
            'all_notes': all_notes,
            'add_note_form': form,
        }

        return render(request, 'notes.html', context)

    else:
        return render(request, 'index.html')

