# Generated by Django 3.1.7 on 2022-11-21 09:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment', '0007_commenttag_model_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commenttag',
            old_name='model_file',
            new_name='report_file',
        ),
    ]
