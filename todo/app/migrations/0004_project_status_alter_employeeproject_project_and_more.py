# Generated by Django 4.0 on 2024-02-12 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_employeeproject_project_task_taskassignment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('TO DO', 'To Do'), ('IN PR0GRESS', 'In Progress'), ('COMPLETED', 'Completed')], default='TODO', max_length=20),
        ),
        migrations.AlterField(
            model_name='employeeproject',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.project'),
        ),
        migrations.AlterField(
            model_name='employeeproject',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user'),
        ),
    ]
