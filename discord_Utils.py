
import requests

def send_discord_notification(message):
    hook = 'https://discord.com/api/webhooks/1319968423836520509/IjkQyORRP21jWBmvKYeZPu3Wj4YlsyQKAU3Ok9I-tpv8sqFOdqPxFO4siS6ScslAUieo'


    payload = {"content": message}  # The message content
    response = requests.post(hook, json=payload)
    if response.status_code == 204:
        print("Notification sent successfully!")
    else:
        print(f"Failed to send notification: {response.status_code} - {response.text}")

