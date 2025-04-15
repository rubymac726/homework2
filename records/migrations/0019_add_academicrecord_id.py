from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('records', '0018_alter_academicrecord_academic_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicrecord',
            name='student',
            field=models.ForeignKey(on_delete=models.CASCADE, 
                                 related_name='academic_records',
                                 to='records.studentprofile',
                                 to_field='student_id'),
        ),
    ]