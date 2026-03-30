from django.db import migrations


def populate_planned_folders_data(apps, schema_editor):
    '''
    Populate planned_folders data based on plant name mapping.
    '''
    ScheduledTime = apps.get_model('handler_default_data', 'ScheduledTime')

    # Define the planned_folders mapping (from user attachment)
    planned_folders_data = {
        'Airoli': 2,
        'Baroda': 1,
        'Bhosari': 1,
        'Bommasandra': 2,
        'Butibori': 1,
        'Chemmencherry': 2,
        'Chinhat': 1,
        'Kandivali': 2,
        'Manesar': 1,
        'Nacharam': 2,
        'Sahibabad': 2,
        'Saltlake': 1,
        'Trivandrum': 1,
        'Vejalpur': 1,
    }

    for plant_name, planned_folders in planned_folders_data.items():
        try:
            scheduled_time_obj = ScheduledTime.objects.get(plant_name=plant_name)
            scheduled_time_obj.planned_folders = planned_folders
            scheduled_time_obj.save()
            print(f"Updated {plant_name} with planned_folders: {planned_folders}")
        except ScheduledTime.DoesNotExist:
            print(f"Plant {plant_name} not found in database")
        except Exception as e:
            print(f"Error updating {plant_name}: {e}")


def reverse_populate_planned_folders_data(apps, schema_editor):
    '''
    Reverse operation - set all planned_folders back to default value 1.
    '''
    ScheduledTime = apps.get_model('handler_default_data', 'ScheduledTime')
    ScheduledTime.objects.update(planned_folders=1)


class Migration(migrations.Migration):
    dependencies = [
        ('handler_default_data', '0006_add_planned_folders'),
    ]

    operations = [
        migrations.RunPython(
            populate_planned_folders_data,
            reverse_populate_planned_folders_data
        ),
    ]