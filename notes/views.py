import json
import os
from io import BytesIO

from django.core.signing import BadSignature
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from taggit.models import Tag
from .models import Note, AddNoteForm


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """

    s_url = settings.STATIC_URL  # Typically /static/
    s_root = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    m_url = settings.MEDIA_URL  # Typically /static/media/
    m_root = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

    if uri.startswith(m_url):
        path = os.path.join(m_root, uri.replace(m_url, ""))
    elif uri.startswith(s_url):
        path = os.path.join(s_root, uri.replace(s_url, ""))
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (s_url, m_url)
        )
    return path


def render_to_pdf(template_src, context_dict={}):
    """
    Helper function to generate pdf from html
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error Rendering PDF", status=400)


@login_required
def generate_pdf(request, slug):
    note = get_object_or_404(Note, slug=slug)
    if note.user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('notes')
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
    add_note_form = AddNoteForm()
    context = {
        'note_detail': note,
    }
    pdf = render_to_pdf('note_as_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "{}.pdf".format(note.slug)
        content = "inline; filename={}".format(filename)
        content = "attachment; filename={}".format(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


# @login_required
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


@login_required
def get_note_details(request, slug):
    note = get_object_or_404(Note, slug=slug)
    if note.user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('notes')

    notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
    add_note_form = AddNoteForm()

    absolute_url = request.build_absolute_uri(note.get_absolute_url())

    context = {
        'notes': notes,
        'note_detail': note,
        'add_note_form': add_note_form,
        'absolute_url': absolute_url
    }
    return render(request, 'note_details.html', context)


@login_required
def edit_note_details(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if note.user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('notes')
    if request.method == 'POST':
        form = AddNoteForm(request.POST, instance=note)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user = request.user
            form_data.save()
            form.save_m2m()
            return redirect('note_detail', slug=note.slug)
    else:
        form = AddNoteForm(initial={
            'note_title': note.note_title,
            'note_content': note.note_content,
            'tags': ','.join([i.slug for i in note.tags.all()]),
        }, instance=note)
        return render(request, 'modals/edit_note_modal.html', {'form': form})


@login_required
def confirm_delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if note.user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('notes')
    # note.delete()
    context = {
        'note_detail': note,
    }
    return render(request, 'modals/delete_note_modal.html', context)


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if note.user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('notes')
    note.delete()
    messages.success(request, 'Note deleted successfully!')
    return redirect('notes')


def search_note(request):
    note_json = {'slug': None, 'label': None, 'value': None}
    q = request.GET.get('term')
    notes = Note.objects.filter(
        note_title__icontains=q,
        user=request.user
    )[:10]
    results = []
    for note in notes:
        note_json = {'slug': note.slug, 'label': note.note_title, 'value': note.note_title}
        results.append(note_json)
    data = json.dumps(results)
    return HttpResponse(data)


def get_shareable_link(request, signed_pk):
    try:
        pk = Note.signer.unsign(signed_pk)
        note = Note.objects.get(pk=pk)
        context = {
            'note_detail': note
        }
        return render(request, 'shared_note.html', context)
    except (BadSignature, Note.DoesNotExist):
        raise Http404('No Order matches the given query.')


def get_all_notes_tags(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    # Filter posts by tag name
    all_notes = Note.objects.filter(tags=tag, user=request.user)
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
    add_note_form = AddNoteForm()
    context = {
        'tag': tag,
        'all_notes': all_notes,
        'notes': notes,
        'add_note_form': add_note_form
    }
    return render(request, 'tags.html', context)
