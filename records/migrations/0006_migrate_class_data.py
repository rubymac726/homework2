from django.db import migrations

def forwards(apps, schema_editor):
    StudentProfile = apps.get_model('records', 'StudentProfile')
    StudentClassHistory = apps.get_model('records', 'StudentClassHistory')
    
    for student in StudentProfile.objects.all():
        StudentClassHistory.objects.create(
            student=student,
            academic_year=student.academic_year,
            form_class=student.form_class
        )

class Migration(migrations.Migration):
    dependencies = [
        # Replace with the name of your previous migration
        ('records', '0005_studentclasshistory'),  
    ]
    
    operations = [
        migrations.RunPython(forwards),
    ]
