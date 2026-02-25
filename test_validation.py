from proxy.app.schemas.meeting_summary import MeetingSummaryRequest
from pydantic import ValidationError

def test_validation():
    print("--- Test 1: Valid Request ---")
    try:
        req = MeetingSummaryRequest(meeting_id="123", transcript="Hello", language="en")
        print("✅ Valid request accepted")
    except ValidationError as e:
        print(f"❌ Should not fail: {e}")

    print("\n--- Test 2: Invalid Language ---")
    try:
        req = MeetingSummaryRequest(meeting_id="123", transcript="Hello", language="de")
        print("❌ Invalid language accepted (FAIL)")
    except ValidationError:
        print("✅ Invalid language rejected")

    print("\n--- Test 3: Empty Transcript ---")
    try:
        req = MeetingSummaryRequest(meeting_id="123", transcript="", language="fr")
        print("❌ Empty transcript accepted (FAIL)")
    except ValidationError:
        print("✅ Empty transcript rejected")

if __name__ == "__main__":
    test_validation()
