from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ScheduledTime


def get_plant_schedule(request, plant_name):
    """
    API endpoint to get schedule for a specific plant.
    """
    schedule = ScheduledTime.get_schedule_by_plant(plant_name)

    if schedule:
        return JsonResponse({
            'plant_name': schedule.plant_name,
            'scheduled_lprs': schedule.scheduled_lprs.strftime('%H:%M:%S'),
            'scheduled_print_start': schedule.scheduled_print_start.strftime('%H:%M:%S'),
            'duration_minutes': schedule.lprs_to_print_duration.total_seconds() / 60
        })
    else:
        return JsonResponse({'error': 'Plant schedule not found'}, status=404)


def list_all_schedules(request):
    """
    List all active plant schedules.
    """
    schedules = ScheduledTime.get_active_schedules()

    schedule_list = []
    for schedule in schedules:
        schedule_list.append({
            'plant_name': schedule.plant_name,
            'scheduled_lprs': schedule.scheduled_lprs.strftime('%H:%M:%S'),
            'scheduled_print_start': schedule.scheduled_print_start.strftime('%H:%M:%S'),
        })

    return JsonResponse({'schedules': schedule_list})


