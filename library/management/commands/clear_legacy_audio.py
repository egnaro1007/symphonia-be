from django.core.management.base import BaseCommand
from library.models import Song
from django.db import models

class Command(BaseCommand):
    help = 'Clear legacy audio field after migration to quality-based structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be cleared without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no fields will be cleared'))
        
        # Get all songs with legacy audio files but have quality-specific files
        songs = Song.objects.filter(
            audio__isnull=False
        ).exclude(audio='').filter(
            # At least one quality-specific file exists
            models.Q(audio_lossless__isnull=False) |
            models.Q(audio_320kbps__isnull=False) |
            models.Q(audio_128kbps__isnull=False)
        )
        
        self.stdout.write(f'Found {songs.count()} songs with legacy audio field that can be cleared')
        
        cleared_count = 0
        for song in songs:
            try:
                self.stdout.write(f'Song ID {song.id}: "{song.title}"')
                self.stdout.write(f'  Legacy audio: {song.audio.name if song.audio else "None"}')
                self.stdout.write(f'  Available qualities: {", ".join(song.get_available_qualities())}')
                
                if not dry_run:
                    # Clear the legacy audio field
                    song.audio = None
                    song.save()
                    cleared_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Cleared legacy audio field'))
                else:
                    self.stdout.write(f'  → Would clear legacy audio field')
                
                self.stdout.write('')  # Empty line for readability
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error clearing song {song.id}: {str(e)}'))
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Cleared legacy audio field for {cleared_count} songs'))
        else:
            self.stdout.write(self.style.WARNING('DRY RUN completed - no changes made')) 