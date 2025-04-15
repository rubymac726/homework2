from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('records', '0019_add_academicrecord_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicrecord',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]