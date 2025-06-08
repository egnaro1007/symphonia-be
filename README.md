# Symphonia - Music Streaming Backend

Symphonia is a feature-rich music streaming service backend built with Django and Django REST Framework. This backend provides APIs for user management, music playback, playlist creation, friend connections, and more.

## Features

### User Management
- User registration and authentication with JWT
- Profile management (personal info, profile pictures)
- Friend connections (send/accept/reject friend requests, unfriend)
- Password management

### Music Library
- Song management with multiple audio quality options (lossless, 320kbps, 128kbps)
- Artist and album organization
- Cover art and metadata support
- Lyrics support with timestamped data

### Playlists
- Create and manage personal playlists
- Add/remove songs from playlists
- Playlist cover images
- Sharing permissions (private, friends-only, public)

### Social Features
- Friend relationships
- Shared playlists
- User activity tracking

### Listening Experience
- Track listening history
- Song likes/favorites
- Playback position tracking

## Getting Started

### Prerequisites
- Python 3.x
- Django 5.2
- Pip (Python package manager)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/symphonia-be.git
   cd symphonia-be
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   # On Linux/macOS
   python -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Media Management
The system uses a structured media organization system:

- Profile pictures: `media/images/profile_pictures/`
- Song files:
  - Lossless: `media/songs/lossless/`
  - 320kbps: `media/songs/320kbps/`
  - 128kbps: `media/songs/128kbps/`
- Cover art: `media/images/cover_art/`
- Playlist covers: `media/images/playlist_covers/`

## API Documentation
API documentation is available through DRF Spectacular:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema`

## Project Structure
```
symphonia-be/
├── authentication/           # User authentication app
│   ├── migrations/
│   ├── models.py             # User profiles, friendships
│   ├── serializers.py
│   ├── views.py              # Authentication endpoints
│   └── ...
├── library/                  # Music library app
│   ├── migrations/
│   ├── models.py             # Songs, artists, albums, playlists
│   ├── serializers.py
│   ├── views.py              # Music library endpoints
│   └── ...
├── media/                    # Media storage
│   ├── images/
│   │   ├── cover_art/
│   │   ├── playlist_covers/
│   │   └── ...
│   └── songs/
│       ├── lossless/
│       ├── 320kbps/
│       └── 128kbps/
├── symphonia/                # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── manage.py
└── requirements.txt
```

## Technologies Used
- [Django](https://www.djangoproject.com/) - Web framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API toolkit
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) - JWT authentication
- [Pillow](https://python-pillow.org/) - Image processing
- [DRF Spectacular](https://drf-spectacular.readthedocs.io/) - API documentation

## Environment Variables
The project uses Django's default settings for development. For production, consider setting these environment variables:

- `DEBUG` - Set to False in production
- `ALLOWED_HOSTS` - List of allowed hosts
- `DATABASE_URL` - Database connection string (if not using SQLite)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.