#!/bin/bash

# Clone the repository (first time only)
git clone https://github.com/rayklanderman/sauti_ya_mwanainchi.git
cd sauti_ya_mwanainchi

# Pull latest changes (for subsequent deployments)
git pull origin main

# Create and activate virtual environment
mkvirtualenv --python=/usr/bin/python3.11 sauti_env
workon sauti_env

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "Setting up environment variables..."
echo "export DEBUG=False" >> ~/.virtualenvs/sauti_env/bin/postactivate
echo "export SECRET_KEY='your-secret-key-here'" >> ~/.virtualenvs/sauti_env/bin/postactivate
echo "export DATABASE_URL='postgresql://username:password@host:5432/dbname'" >> ~/.virtualenvs/sauti_env/bin/postactivate
echo "export ALLOWED_HOSTS='.pythonanywhere.com'" >> ~/.virtualenvs/sauti_env/bin/postactivate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (first time only)
# python manage.py createsuperuser

# Reload the web app
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
