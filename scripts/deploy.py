import os
import requests
from datetime import datetime

def deploy_to_pythonanywhere():
    token = os.environ['PA_TOKEN']
    username = 'DevRay'
    domain = f'{username}.pythonanywhere.com'
    api_base = f'https://www.pythonanywhere.com/api/v0/user/{username}'
    headers = {'Authorization': f'Token {token}'}

    # Update from Git
    print("Pulling latest code...")
    response = requests.post(
        f'{api_base}/consoles/',
        headers=headers,
        json={
            "executable": "bash",
            "working_directory": "/home/DevRay/sauti_ya_mwanainchi",
            "input": "git pull origin main"
        }
    )
    response.raise_for_status()

    # Install requirements
    print("Installing requirements...")
    response = requests.post(
        f'{api_base}/consoles/',
        headers=headers,
        json={
            "executable": "bash",
            "working_directory": "/home/DevRay/sauti_ya_mwanainchi",
            "input": "source sauti_env/bin/activate && pip install -r requirements.txt"
        }
    )
    response.raise_for_status()

    # Collect static
    print("Collecting static files...")
    response = requests.post(
        f'{api_base}/consoles/',
        headers=headers,
        json={
            "executable": "bash",
            "working_directory": "/home/DevRay/sauti_ya_mwanainchi",
            "input": "source sauti_env/bin/activate && python manage.py collectstatic --noinput"
        }
    )
    response.raise_for_status()

    # Run migrations
    print("Running migrations...")
    response = requests.post(
        f'{api_base}/consoles/',
        headers=headers,
        json={
            "executable": "bash",
            "working_directory": "/home/DevRay/sauti_ya_mwanainchi",
            "input": "source sauti_env/bin/activate && python manage.py migrate"
        }
    )
    response.raise_for_status()

    # Reload the web app
    print("Reloading web app...")
    response = requests.post(
        f'{api_base}/webapps/{domain}/reload/',
        headers=headers
    )
    response.raise_for_status()

    print(f"Deployment completed at {datetime.now()}")

if __name__ == '__main__':
    deploy_to_pythonanywhere()
