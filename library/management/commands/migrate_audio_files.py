import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from library.models import Song

class Command(BaseCommand):
    help = 'Migrate existing audio files to quality-based structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be migrated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no files will be moved'))
        
        # Get all songs with legacy audio files
        songs = Song.objects.filter(audio__isnull=False).exclude(audio='')
        
        self.stdout.write(f'Found {songs.count()} songs with audio files to migrate')
        
        for song in songs:
            try:
                # Get the current audio file path
                current_audio_path = song.audio.path
                current_audio_name = os.path.basename(current_audio_path)
                
                # Get file extension
                file_extension = os.path.splitext(current_audio_name)[1]
                
                # Create new filename using song ID
                new_filename = f"{song.id}{file_extension}"
                
                # Define new path for 320kbps quality (since you mentioned existing files are 320kbps)
                new_audio_path = os.path.join(settings.MEDIA_ROOT, 'songs', '320kbps', new_filename)
                
                self.stdout.write(f'Song ID {song.id}: "{song.title}"')
                self.stdout.write(f'  From: {current_audio_path}')
                self.stdout.write(f'  To: {new_audio_path}')
                
                if not dry_run:
                    # Ensure the destination directory exists
                    os.makedirs(os.path.dirname(new_audio_path), exist_ok=True)
                    
                    # Copy the file to new location (we copy instead of move to be safe)
                    shutil.copy2(current_audio_path, new_audio_path)
                    
                    # Update the song's audio_320kbps field
                    song.audio_320kbps = f'songs/320kbps/{new_filename}'
                    song.save()
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Successfully migrated'))
                else:
                    self.stdout.write(f'  → Would copy to: {new_audio_path}')
                    self.stdout.write(f'  → Would update audio_320kbps field')
                
                self.stdout.write('')  # Empty line for readability
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error migrating song {song.id}: {str(e)}'))
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Migration completed for {songs.count()} songs'))
            self.stdout.write('')
            self.stdout.write('IMPORTANT: After verifying the migration was successful, you can:')
            self.stdout.write('1. Remove the old audio files from media/songs/ (not in subdirectories)')
            self.stdout.write('2. Clear the legacy "audio" field by running: python manage.py clear_legacy_audio')
        else:
            self.stdout.write(self.style.WARNING('DRY RUN completed - no changes made')) 