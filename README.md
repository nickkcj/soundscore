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
- **Database**: PostgreSQL  
- **Containerization**: Docker 

---

## 🐳 Running with Docker

If you prefer not to install anything locally, you can spin up the app using Docker:

```bash
# Step 1: Build the image
docker-compose build

# Step 2: Run the containers
docker-compose up
```

The app will be available at `http://localhost:8000`.

> ℹ️ **Note**: This project uses a **PostgreSQL** database.  
> To run the app successfully, you need to provide your own database credentials via a `.env` file.  
> The database is not publicly accessible, so the listed demo users (`demo1`, `demo2`, `demo3`) will **not work by default** unless you have access to the same database instance.  
> You can still create your own users after setting up the app locally.


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

### 4. Add your environment variables

Create a `.env` file in the root folder and add:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```
> 🛑 **Important:** You need to provide your own PostgreSQL database or ask the maintainer for access credentials.
> The project does not include a working `.env` file or a public demo database for security reasons.

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
│   ├── .env                   # Environment variables (e.g., Spotify API keys, DB settings)
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
