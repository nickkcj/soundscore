# Generated by Django 5.2 on 2025-04-13 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soundscore', '0004_user_groups_user_is_active_user_is_staff_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
