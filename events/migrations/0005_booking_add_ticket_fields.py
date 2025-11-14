# Generated manually for ticket fields

from django.db import migrations, models
import uuid

def generate_ticket_ids(apps, schema_editor):
    Booking = apps.get_model('events', 'Booking')
    for booking in Booking.objects.all():
        if not booking.ticket_id:
            booking.ticket_id = str(uuid.uuid4())
            booking.save()

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_alter_event_category_alter_event_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='number_of_seats',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='booking',
            name='ticket_id',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
        migrations.RunPython(generate_ticket_ids),
        migrations.AlterField(
            model_name='booking',
            name='ticket_id',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
