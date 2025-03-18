import requests
import base64
from .models import Profile

def refresh_fitbit_token(user):
    profile = Profile.objects.filter(user=user).first()
    if not profile or not profile.fitbit_refresh_token:
        return None

    CLIENT_ID = "23Q39R"
    CLIENT_SECRET = "827dc7361f76cbc28d06236e40374945"
    token_url = "https://api.fitbit.com/oauth2/token"

    # Encodage des credentials en base64
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"}

    data = {
        "grant_type": "refresh_token",
        "refresh_token": profile.fitbit_refresh_token
    }
    print("Refreshing Fitbit token...")
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        profile.fitbit_access_token = tokens["access_token"]
        profile.fitbit_refresh_token = tokens["refresh_token"]
        profile.save()
        return tokens["access_token"]
    
    return None
