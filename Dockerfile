# Use the official Python image from the Docker Hub
FROM python:3.13-slim

# Set the working directory to /soundscore (the root of your project)
WORKDIR /soundscore

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev && apt-get clean

# Install pip and the required Python dependencies
COPY requirements.txt /soundscore/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /soundscore/

# Set environment variables (use .env if you have one)
ENV PYTHONUNBUFFERED=1

# Run migrations and collect static files before starting the server
# Use exec form (JSON array) for CMD to handle signals properly
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
