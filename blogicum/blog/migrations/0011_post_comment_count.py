# Generated by Django 3.2.16 on 2025-02-22 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_post_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comment_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество комментариев'),
        ),
    ]
