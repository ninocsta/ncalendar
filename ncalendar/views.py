from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def calendar_page(request):
    # Render the calendar-specific template which imports FullCalendar and minicalendar assets
    return render(request, "calendar.html")
