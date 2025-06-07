from django.db import migrations


def normalize_email_data(apps, schema_editor):
    """
    First clean duplicate emails, then convert empty email strings to None
    """
    UserProfile = apps.get_model('authentication', 'UserProfile')
    
    # Step 1: Handle empty emails first - convert them to None
    UserProfile.objects.filter(email='').update(email=None)
    
    # Step 2: Find and resolve duplicate emails
    # Get all non-null, non-empty emails
    profiles_with_emails = UserProfile.objects.exclude(email__isnull=True).exclude(email='')
    
    seen_emails = set()
    for profile in profiles_with_emails:
        if profile.email in seen_emails:
            # This is a duplicate, clear it (set to None)
            profile.email = None
            profile.save()
        else:
            seen_emails.add(profile.email)


def reverse_normalize_email_data(apps, schema_editor):
    """
    Reverse migration - convert None emails back to empty strings
    """
    UserProfile = apps.get_model('authentication', 'UserProfile')
    
    # Update all profiles with None email to empty strings
    UserProfile.objects.filter(email__isnull=True).update(email='')


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_alter_userprofile_email'),
    ]

    operations = [
        migrations.RunPython(normalize_email_data, reverse_normalize_email_data),
    ] 