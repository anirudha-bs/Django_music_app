# Generated by Django 3.0.6 on 2020-08-16 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_auto_20200816_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='album_logo',
            field=models.FileField(default='avatar_2x.png', upload_to=''),
        ),
    ]
