# Generated by Django 3.0.6 on 2020-08-19 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_auto_20200816_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='album_logo',
            field=models.FileField(default='avatar.jpg', upload_to=''),
        ),
    ]
