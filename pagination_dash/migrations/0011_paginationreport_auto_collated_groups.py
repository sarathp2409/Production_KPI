from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagination_dash', '0010_gnpinformation_et_b1_gnpinformation_et_b2'),
    ]

    operations = [
        migrations.AddField(
            model_name='paginationreport',
            name='auto_collated_groups',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of auto-collated book groups (each group is a list of book names)'
            ),
        ),
    ]
