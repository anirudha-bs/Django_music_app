# Generated by Django 3.0.6 on 2020-08-16 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_auto_20200816_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='album_logo',
            field=models.FileField(default='avatar.png', upload_to=''),
        ),
    ]
