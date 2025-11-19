from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def calendar_page(request):
    return render(request, "ncalendar/calendar.html")
