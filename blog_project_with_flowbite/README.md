# Django Blog Project (Portfolio)

A blog website I built using Django and Flowbite. Users can write posts, follow others, and interact with the community. I added cool features like caching for speed and rate limiting for security!

![Project Demo](demo.gif)

## Features

- User signup and login
- Create and edit blog posts
- Like and comment on posts
- Follow your favorite writers
- Get notifications by email
- Search for posts and users
- User profiles with stats
- Mobile friendly design
- Rate limiting to prevent spam
- Caching to make it fast
- Track user sessions
- Contact form
- Debug toolbar in development

## Tech Stack

- Django 4.x
- Flowbite + Tailwind CSS
- SQLite
- JavaScript
- django-ratelimit (for security)
- django-redis (for making things faster)
- django-user-sessions (for tracking users)
- django-debug-toolbar (for development)
- django-user-agents (for device detection)
- Pillow (for handling images)
- python-dotenv (for settings)

## Setup Guide

1. Clone project:
```bash
git clone https://github.com/maruf-hossen-5566/blog-project.git
cd blog-project
```

2. Setup Python:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

3. Setup environment:
```bash
# Copy .env.example to .env and edit it
copy .env.example .env
```

Required environment variables:
```
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the server:
```bash
python manage.py runserver
```

## Project Structure

```
blog_project/
├── auth_app/        # User login and signup
├── blog_app/        # Blog posts and drafts
├── comment_app/     # Comments system
├── contact_app/     # Contact form
├── email_app/       # Email notifications
├── like_app/        # Post likes
├── me_app/          # User dashboard
├── notification_app/# Notifications
├── profile_app/     # User profiles
├── search_app/      # Search posts and users
├── suggestion_app/  # Post suggestions
└── utils/           # Helper functions
```

## Main Features

### Posts
- Write blog posts with images
- Save drafts before publishing
- Like and comment on posts
- Follow your favorite topics
- Fast loading with caching

### Users
- Follow other writers
- Get email notifications
- See your stats
- Customize your profile
- Protected against spam with rate limiting
- Track user sessions
- Works on all devices

### Search & Contact
- Find posts and users
- Browse by topics
- See what's trending
- Contact form for feedback
- Smart post suggestions

## What I Learned

- Building a Django project from scratch
- Working with Django's auth system
- Making a responsive UI with Flowbite
- Database queries and models
- File uploads and image handling
- Form handling and validation
- User authentication and sessions
- Working with multiple Django apps
- Using caching to make sites faster
- Adding security with rate limiting
- Sending emails with Django
- Making a search feature
- Using the debug toolbar
- Working with environment variables
- Detecting user devices

## Author

Maruf Hossen
- GitHub: [Maruf Hossen](https://github.com/maruf-hossen-5566)
- LinkedIn: [Maruf Hossen](https://www.linkedin.com/in/maruf-hossen-777595339/)