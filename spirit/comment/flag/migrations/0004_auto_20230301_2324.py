# Generated by Django 3.1.14 on 2023-03-01 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment_flag', '0003_alter_commentflag_id_alter_flag_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentflag',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='flag',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
