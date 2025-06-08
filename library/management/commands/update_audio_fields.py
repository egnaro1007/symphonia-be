import os
from django.core.management.base import BaseCommand
from django.conf import settings
from library.models import Song

class Command(BaseCommand):
    help = 'Update audio quality fields based on existing files in media/songs directories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be updated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no database changes will be made'))
        
        # Quality directories to check
        qualities = {
            'lossless': 'audio_lossless',
            '320kbps': 'audio_320kbps',
            '128kbps': 'audio_128kbps'
        }
        
        updated_count = 0
        
        # Get all songs
        songs = Song.objects.all()
        self.stdout.write(f'Checking {songs.count()} songs for available audio files...')
        
        for song in songs:
            song_updated = False
            self.stdout.write(f'\nSong ID {song.id}: "{song.title}"')
            
            for quality_dir, field_name in qualities.items():
                # Check for common audio file extensions
                extensions = ['.mp3', '.flac', '.wav', '.m4a']
                audio_file_path = None
                
                for ext in extensions:
                    file_path = os.path.join(settings.MEDIA_ROOT, 'songs', quality_dir, f'{song.id}{ext}')
                    if os.path.exists(file_path):
                        audio_file_path = f'songs/{quality_dir}/{song.id}{ext}'
                        break
                
                if audio_file_path:
                    current_value = getattr(song, field_name)
                    if not current_value or not current_value.name:
                        self.stdout.write(f'  → Found {quality_dir} file: {audio_file_path}')
                        if not dry_run:
                            setattr(song, field_name, audio_file_path)
                            song_updated = True
                        else:
                            self.stdout.write(f'    Would update {field_name} field')
                    else:
                        self.stdout.write(f'  ✓ {quality_dir} already set: {current_value.name}')
                else:
                    self.stdout.write(f'  - No {quality_dir} file found')
            
            if song_updated and not dry_run:
                song.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Updated song {song.id}'))
        
        if not dry_run:
            self.stdout.write(f'\n{self.style.SUCCESS(f"Successfully updated {updated_count} songs")}')
        else:
            self.stdout.write(f'\n{self.style.WARNING("DRY RUN completed - no changes made")}') 