# Generated by Django 4.1.5 on 2023-03-09 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment', '0012_auto_20230301_2324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='commenttag',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
