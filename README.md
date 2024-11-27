# Sauti ya Mwananchi

## Public Participation Platform for Kenya's Counties

Sauti ya Mwananchi is a digital platform designed to enhance public participation in legislative processes across Kenya's 47 counties. This platform aligns with SDG 16 (Peace, Justice and Strong Institutions) by promoting inclusive, participatory decision-making at the county level.

### Features

- County-specific legislative tracking
- Public comment submission system
- Real-time notifications for new bills and policies
- Document repository for bills and policies
- User authentication and profile management
- Analytics dashboard for participation metrics
- Mobile-responsive design

### Technical Requirements

- Python 3.8+
- Django 4.2.7
- PostgreSQL
- Modern web browser

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/sauti_ya_mwananchi.git
cd sauti_ya_mwananchi
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. Create superuser
```bash
python manage.py createsuperuser
```

6. Run the development server
```bash
python manage.py runserver
```

### Deployment

#### Option 1: PythonAnywhere (Recommended)

1. Sign up for a PythonAnywhere account at https://www.pythonanywhere.com/

2. Create a new web app:
   - Choose Manual Configuration
   - Select Python 3.11
   - Note your domain name (username.pythonanywhere.com)

3. Set up your virtual environment:
```bash
mkvirtualenv --python=/usr/bin/python3.11 sauti_env
pip install -r requirements.txt
```

4. Configure your web app:
   - Go to the Web tab
   - Set the virtual environment path: /home/yourusername/.virtualenvs/sauti_env
   - Set the WSGI configuration file
   - Add your environment variables in the "Environment variables" section:
     ```
     DATABASE_URL=postgresql://username:password@host:port/dbname
     SECRET_KEY=your_secret_key
     DEBUG=False
     ALLOWED_HOSTS=yourdomain.pythonanywhere.com
     ```

5. Set up PostgreSQL database:
   - Create a new PostgreSQL database in PythonAnywhere
   - Update DATABASE_URL in environment variables
   - Run migrations:
     ```bash
     python manage.py migrate
     ```

6. Set up static files:
   - Add in your web app configuration:
     ```
     /static/ -> /home/yourusername/sauti_ya_mwananchi/staticfiles
     /media/ -> /home/yourusername/sauti_ya_mwananchi/media
     ```
   - Run collectstatic:
     ```bash
     python manage.py collectstatic
     ```

7. Reload your web app

#### Option 2: Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Add vercel.json to your project root:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "sauti_ya_mwananchi/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "sauti_ya_mwananchi/wsgi.py"
    }
  ]
}
```

3. Deploy:
```bash
vercel
```

4. Set up environment variables in Vercel dashboard:
   - DATABASE_URL
   - SECRET_KEY
   - DEBUG
   - ALLOWED_HOSTS

5. Connect to external PostgreSQL service (e.g., Supabase, Railway)

### Production Considerations

1. Security:
   - Keep DEBUG=False in production
   - Use strong SECRET_KEY
   - Enable HTTPS
   - Configure ALLOWED_HOSTS properly
   - Set up proper CORS headers
   - Enable CSP (Content Security Policy)

2. Performance:
   - Enable caching with django-redis
   - Use whitenoise for static files
   - Configure database connection pooling
   - Set up proper logging

3. Monitoring:
   - Set up Sentry for error tracking
   - Configure Django Debug Toolbar in development
   - Set up performance monitoring

4. Backup:
   - Regular database backups
   - Automated backup scheduling
   - Secure backup storage

### Environment Variables

Required environment variables for production:
```
DATABASE_URL=postgresql://username:password@host:port/dbname
SECRET_KEY=your_secure_secret_key
DEBUG=False
ALLOWED_HOSTS=your.domain.com
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
REDIS_URL=redis://localhost:6379/1
SENTRY_DSN=your-sentry-dsn
```

### Contributing

We welcome contributions! Please read our contributing guidelines before submitting pull requests.

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Support

For support, please open an issue or contact the development team.
