from django.db import migrations


def clean_duplicate_emails(apps, schema_editor):
    """
    Clean up duplicate emails by setting empty string for duplicates
    """
    UserProfile = apps.get_model('authentication', 'UserProfile')
    
    # Find all profiles with non-empty emails
    profiles_with_emails = UserProfile.objects.exclude(email='').exclude(email__isnull=True)
    
    # Group by email
    seen_emails = set()
    for profile in profiles_with_emails:
        if profile.email in seen_emails:
            # This is a duplicate, clear it
            profile.email = ''
            profile.save()
        else:
            seen_emails.add(profile.email)


def reverse_clean_duplicate_emails(apps, schema_editor):
    """
    This is a one-way migration, no reverse operation
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_userprofile_birth_date_userprofile_gender'),
    ]

    operations = [
        migrations.RunPython(clean_duplicate_emails, reverse_clean_duplicate_emails),
    ] 