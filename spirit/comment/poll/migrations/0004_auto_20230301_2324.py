# Generated by Django 3.1.14 on 2023-03-01 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment_poll', '0003_alter_commentpoll_id_alter_commentpollchoice_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentpoll',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='commentpollchoice',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='commentpollvote',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
