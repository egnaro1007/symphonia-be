# Generated by Django 5.2 on 2025-04-14 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_remove_album_songs_remove_artist_songs_song_album_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='album',
            name='artist',
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ManyToManyField(related_name='albums', to='library.artist'),
        ),
    ]
