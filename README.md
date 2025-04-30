# 🎧 SoundScore

Welcome to **SoundScore** – your personal musical diary!  
Think **Letterboxd**, but for music albums.  
Discover, review, rate, and discuss albums with others — all in one platform built for music lovers.

---

## ✨ Features

- 🔍 Search albums by name or artist using the **Spotify API**
- ⭐ Rate and review albums (1 to 5 stars)
- 🧑‍🤝‍🧑 Find and follow other music lovers
- 💬 Discuss your favorite records
- ❤️ Favorite albums and build your musical identity
- 🗞️ View an interactive **feed** of reviews and ratings from users
- 🤖 Use our AI-powered **chatbot** to get information from the database
- 🔐 Secure authentication system
- 🛠️ Edit your account information
- 📸 Upload profile pictures

---

## 🛠️ Tech Stack

- **Backend**: Django (Python)
- **Frontend**: Django Templates with Tailwind
- **API Integration**: Spotify API, Gemini
- **Database**: PostgreSQL
- **Containerization**: Docker
- **AI Chatbot**: Gemini API

---

## 🐳 Running with Docker

If you prefer not to install anything locally, you can spin up the app using Docker:

```bash
# Step 1: Build the image
docker-compose build

# Step 2: Run the containers
docker-compose up
```

The app will be available at [http://localhost:8000](http://localhost:8000)

> ℹ️ **Note**: This project uses a PostgreSQL database.  
> You must provide your own database credentials via a `.env` file.  
> Demo users (`demo1`, `demo2`, `demo3`) won't work unless you connect to the same database instance.  
> You can create your own account after setting up the app locally.

---

## 🧪 Local Setup (Optional)

If you're not using Docker, follow these steps:

```bash
# 1. Clone the repo
git clone https://github.com/nickkcj/soundscore.git
cd soundscore

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 4. Add your environment variables

Create a `.env` file in the root folder with:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

🛑 **Important**: You must provide your own PostgreSQL database or ask the maintainer for credentials.  
There is **no public demo DB** for security reasons.

```bash
# 5. Run migrations and start the server
python manage.py migrate
python manage.py runserver
```

---

## 📁 Project Structure

```
soundscore/
├── config/                    # Django project settings
│   ├── .env                   # Environment variables (Spotify, DB)
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── media/                     # Uploaded media (e.g., profile pictures)
│
├── soundscore/                # Main Django app
│   ├── services/              # Spotify + Supabase Communication
│   ├── templates/             # HTML templates
│   ├── static/                # Static files (CSS, JS)
│   ├── urls/
│   ├── views/
│   ├── agent/
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

---

## 🤝 Contributing

Pull requests are welcome!  
If you have suggestions, bug reports, or new feature ideas, open an issue or submit a PR.  
Let’s make music logging even more fun 🎶
