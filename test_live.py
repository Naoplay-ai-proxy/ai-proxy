import requests
import json

url = "http://127.0.0.1:8000/api/v1/meeting-summary"

payload = {
    "meeting_id": "meet-google-xyz",
    "language": "fr",
    "transcript": """
    Michel: Bonjour à tous. Nous devons décider du budget pour le projet Alpha.
    Sarah: Je propose 50k pour commencer.
    Michel: D'accord, validé. Sarah, peux-tu envoyer le mail à la finance avant ce soir ?
    Sarah: C'est noté, je m'en occupe.
    """
}

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ SUCCESS!")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"❌ ERROR {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")
