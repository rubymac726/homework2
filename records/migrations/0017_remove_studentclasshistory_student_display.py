# Generated by Django 4.2.19 on 2025-04-10 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0016_rename_student_name_studentclasshistory_student_display'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentclasshistory',
            name='student_display',
        ),
    ]
