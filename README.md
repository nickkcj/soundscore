# 🎧 SoundScore

Welcome to **SoundScore** – your personal musical diary! Think **Letterboxd**, but for music albums. Discover, review, rate, and discuss albums with others, all in one platform.

## ✨ Features

- 🔍 **Search albums** by name or artist using the Spotify API  
- ⭐ **Rate and review** albums (1 to 5 stars)  
- 🧑‍🤝‍🧑 **Find and follow** other music lovers  
- 💬 **Discuss** your favorite records  
- ❤️ **Favorite albums** and build your musical identity  
- 🔐 **Authentication system**  
- 🛠️ **Edit your account** information  

## 🛠️ Tech Stack

- **Backend**: Django (Python)  
- **Frontend**: Django Templates  
- **API Integration**: Spotify API  
- **Database**: SQLite3  
- **Containerization**: Docker 🐳

---

## 🚀 Running with Docker

If you prefer not to install anything locally, you can spin up the app using Docker:

```bash
# Step 1: Build the image
docker-compose build

# Step 2: Run the containers
docker-compose up
```

The app will be available at `http://localhost:8000`.

> ℹ️ **Note**: The database included in this repo is a **DEMO DB** so you can test the app right away.  
> It contains some existing users and reviews.  
> **Users:** [nickkcj, cuniaa, nickderham] the password is the same for all of them: 123;

---

## 🧪 Local Setup (Optional)

If you're not using Docker, you can still run the app locally:

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

---

## 📁 Project Structure

```bash
soundscore/
├── config/                    # Django project configuration
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
│   │   └── spotify.py
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── db.sqlite3                 # Demo database (optional, for testing)
├── Dockerfile                 # Docker configuration
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── requirements.txt
└── manage.py
```

---

## 🤝 Contributing

Pull requests are welcome! If you have ideas or spot any bugs, feel free to open an issue or contribute directly.
