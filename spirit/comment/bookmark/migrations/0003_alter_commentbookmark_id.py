# Generated by Django 4.1.5 on 2023-02-21 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment_bookmark', '0002_auto_20150828_2003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentbookmark',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
