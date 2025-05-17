# logs/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Event

@login_required
def event_list(request):
    qs = Event.objects.all() 
    paginator = Paginator(qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'events.html', {
        'events': page_obj,
    })


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_detail.html', {
        'event': event,
    })
