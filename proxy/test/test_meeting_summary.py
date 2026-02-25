import sys
import os

# Force Python à trouver le dossier 'proxy'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from proxy.app.schemas.meeting_summary import MeetingSummaryRequest
from pydantic import ValidationError

def run_test():
    print("\n" + "="*30)
    print("TEST TACHE 2 : VALIDATION")
    print("="*30)

    # Scénario 1 : Données valides
    try:
        data = {"meeting_id": "M1", "transcript": "Contenu de test", "language": "fr"}
        MeetingSummaryRequest(**data)
        print("✅ Scénario 1 (Valide) : PASSED")
    except Exception as e:
        print(f"❌ Scénario 1 (Valide) : FAILED - {e}")

    # Scénario 2 : Langue non supportée (ex: espagnol)
    try:
        data = {"meeting_id": "M2", "transcript": "Test", "language": "es"}
        MeetingSummaryRequest(**data)
        print("❌ Scénario 2 (Langue ES) : FAILED (Aurait dû être bloqué)")
    except ValidationError:
        print("✅ Scénario 2 (Langue ES) : PASSED (Bloqué comme prévu)")

    # Scénario 3 : Transcript trop long
    try:
        data = {"meeting_id": "M3", "transcript": "A" * 200001}
        MeetingSummaryRequest(**data)
        print("❌ Scénario 3 (Trop long) : FAILED")
    except ValidationError:
        print("✅ Scénario 3 (Trop long) : PASSED (Bloqué comme prévu)")

if __name__ == "__main__":
    run_test()