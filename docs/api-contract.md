# Meeting Summary API Contract

## Overview
This API exposes a governed AI proxy endpoint used to generate structured meeting summaries.

Endpoint:
POST /meeting-summary

---

## Request

Content-Type: application/json

### Fields

| Field        | Type   | Required | Description |
|--------------|--------|----------|-------------|
| meeting_id   | string | Yes      | Unique meeting identifier |
| transcript   | string | Yes      | Full meeting transcript |
| language     | string | Yes      | Language of the meeting (fr or en) |

---

## Response (200)

| Field        | Type   | Description |
|--------------|--------|-------------|
| meeting_id   | string | Echo of input ID |
| summary      | string | Generated structured summary |
| actions      | array  | List of structured action items |

### Action Item Structure

| Field        | Type   | Description |
|--------------|--------|-------------|
| owner        | string | Responsible person |
| description  | string | Description of the action |

---

## Error Codes

| Code | Meaning |
|------|----------|
| 400  | Bad request |
| 401  | Unauthorized |
| 422  | Validation error |
| 500  | Internal server error |

