from django.shortcuts import render

def calendar_page(request):
    return render(request, "ncalendar/calendar.html")
