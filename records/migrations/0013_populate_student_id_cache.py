from django.db import migrations

def populate_cache(apps, schema_editor):
    StudentClassHistory = apps.get_model('records', 'StudentClassHistory')
    for record in StudentClassHistory.objects.all():
        if record.student:
            record.student_id_cache = record.student.student_id
            record.save()

class Migration(migrations.Migration):
    dependencies = [
        ('records', '0012_studentclasshistory_student_id_cache'),  # Use exact filename
    ]
    
    operations = [
        migrations.RunPython(populate_cache),
    ]