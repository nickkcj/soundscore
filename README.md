# 🎧 SoundScore

Welcome to **SoundScore** – your personal musical diary! Think **Letterboxd**, but for music albums. Discover, review, rate, and discuss albums with others, all in one platform.

## ✨ Features

- 🔍 **Search albums** by name or artist using the Spotify API  
- ⭐ **Rate and review** albums (1 to 5 stars)  
- 🧑‍🤝‍🧑 **Find and follow** other music lovers  
- 💬 **Discuss** your favorite records  
- ❤️ **Favorite albums** and build your musical identity  
- 🔐 **Authentication system** (signup, login, logout)  
- 🛠️ **Edit your account** information  

## 🛠️ Tech Stack

- **Backend**: Django (Python)  
- **Frontend**: Django Templates  
- **API Integration**: Spotify API  
- **Database**: SQLite3   

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/nickkcj/soundscore.git
cd soundscore
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Spotify API keys

Create a `.env` file in the root folder and add:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### 5. Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

## 📁 Project Structure

```bash
soundscore/
├── project/                   # Django project configuration
│   ├── .env                   # Environment variables (e.g., Spotify API keys)
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── media/                     # Uploaded media files (e.g., profile pictures)
│   └── profile_pictures/
│       ├── pfp1.jpg
│       └── ...
│
├── soundscore/                # Main Django app
│   ├── apis/                  # API-related logic
│   │   └── spotify.py         # Spotify API integration
│   │
│   ├── migrations/            # Django migrations (DB schema versions)
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── ...
│   │
│   ├── static/                # Static files (CSS, JS, images)
│   │   ├── css/
│   │   │   └── styles.css
│   │   │
│   │   ├── js/
│   │   │   ├── edit_review.js
│   │   │   └── reviews.js
│   │   │
│   │   └── images/
│   │       ├── album1.jpg
│   │       └── ...
│   │
│   ├── templates/             # HTML templates
│   │   ├── about.html
│   │   ├── home.html
│   │   ├── register.html
│   │   ├── review.html
│   │   └── ...
│   │
│   ├── admin.py               # Django admin configuration
│   ├── apps.py                # App config
│   ├── models.py              # Database models
│   ├── tests.py               # Unit tests
│   ├── urls.py                # App-specific URL routes
│   └── views.py               # Request handling and logic
│
├── requirements.txt           # Python dependencies
└── manage.py                  # Django project runner

```

## 🧪 Tests

Coming soon! 🚧

## 🤝 Contributing

Pull requests are welcome! If you have ideas or spot any bugs, feel free to open an issue or contribute directly.
