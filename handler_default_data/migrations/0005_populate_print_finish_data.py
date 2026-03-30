from django.db import migrations
import csv
import os
from datetime import time


def populate_print_finish_data(apps, schema_editor):
    '''
    Populate scheduled_print_finish data from CSV file.
    '''
    ScheduledTime = apps.get_model('handler_default_data', 'ScheduledTime')

    # Define the data mapping (from your CSV)
    csv_data = {'Airoli': '4:00:00',
                'Baroda': '2:30:00',
                'Bommasandra': '4:00:00',
                'Chemmencherry': '4:00:00',
                'Vejalpur': '4:00:00',
                'Nacharam': '4:15:00',
                'Kandivali': '4:00:00',
                'Saltlake': '4:00:00',
                'Chinhat': '4:00:00',
                'Manesar': '3:00:00',
                'Butibori': '4:00:00',
                'Bhosari': '4:00:00',
                'Sahibabad': '4:00:00',
                'Trivandrum': '2:30:00',
                }

    for plant_name, finish_time in csv_data.items():
        try:
            scheduled_time_obj = ScheduledTime.objects.get(plant_name=plant_name)
            # Parse time string to time object
            if isinstance(finish_time, str):
                hour, minute, second = map(int, finish_time.split(':'))
                scheduled_time_obj.scheduled_print_finish = time(hour, minute, second)
            else:
                scheduled_time_obj.scheduled_print_finish = finish_time

            scheduled_time_obj.save()
            print(f"Updated {plant_name} with finish time {finish_time}")
        except ScheduledTime.DoesNotExist:
            print(f"Plant {plant_name} not found in database")
        except Exception as e:
            print(f"Error updating {plant_name}: {e}")


def reverse_populate_print_finish_data(apps, schema_editor):
    '''
    Reverse operation - set all scheduled_print_finish to None.
    '''
    ScheduledTime = apps.get_model('handler_default_data', 'ScheduledTime')
    ScheduledTime.objects.update(scheduled_print_finish=None)


class Migration(migrations.Migration):
    dependencies = [
        ('handler_default_data', '0003_add_scheduled_print_finish'),
    ]

    operations = [
        migrations.RunPython(
            populate_print_finish_data,
            reverse_populate_print_finish_data
        ),
    ]
