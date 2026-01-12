# Scrum AI Assistant API Reference

This document details the API endpoints available in the Scrum AI Assistant, including their purpose, methods, and example JSON payloads.

## Base URL
`http://localhost:8000`

---

## 1. Create Meeting
**Method:** `POST`
**Endpoint:** `/api/meetings/`
**Description:** Creates a new meeting record. This is the first step in the workflow. It defines which tool (Jira/Azure) and project the meeting is associated with.

**Request Payload:**
```json
{
  "title": "Sprint Planning Sprint 34",
  "ceremony_type": "PLANNING",
  "meeting_date": "2024-03-20T10:00:00",
  "tool_type": "JIRA",
  "project_key": "KAN"
}
```

*   **title**: Name of the meeting.
*   **ceremony_type**: `DAILY_STANDUP`, `PLANNING`, `RETROSPECTIVE`, or `REVIEW`.
*   **meeting_date**: ISO 8601 formatted date string.
*   **tool_type**: `JIRA` (Azure/Trello planned).
*   **project_key**: The Key of the project in Jira (e.g., "KAN", "PROJ") where tasks will be created.

**Response:**
```json
{
  "id": 23,
  "title": "Sprint Planning Sprint 34",
  "status": "CREATED",
  ...
}
```

---

## 2. Add Transcript
**Method:** `POST`
**Endpoint:** `/api/meetings/{meeting_id}/transcript`
**Description:** Adds a text transcript to an existing meeting. This text is what the AI will analyze to find action items.

**Request Payload:**
```json
{
  "transcript": "Okay everyone, welcome to planning. The main goal this sprint is to fix the payment gateway bug. Sarah, you will take lead on that. John, please update the documentation for the API."
}
```

**Response:**
```json
{
  "message": "Transcript added successfully"
}
```

---

## 3. Upload Audio File (Optional)
**Method:** `POST`
**Endpoint:** `/api/meetings/{meeting_id}/upload`
**Description:** Uploads an audio recording of the meeting. The system will transcribe this audio (Mock transcription currently) into text.

**Request Type:** `multipart/form-data`
**Form Fields:**
*   `file`: (Binary file content - .mp3, .wav, .m4a)

**Response:**
```json
{
  "filename": "23_recording.mp3",
  "message": "File uploaded successfully"
}
```

---

## 4. Process Meeting (Trigger Task Creation)
**Method:** `POST`
**Endpoint:** `/api/meetings/{meeting_id}/process`
**Description:** **Crucial Step.** Triggers the background processing pipeline.
1.  **AI Analysis:** Analyzes the transcript (from Step 2 or 3).
2.  **Extraction:** Identifies Decisions, Blockers, and Action Items.
3.  **Integration:** **Creates tasks in Jira** automatically for each Action Item found.

**Request Payload:** None (Empty JSON)

**Response:**
```json
{
  "started": true,
  "meeting_id": 23
}
```
*Note: This is asynchronous. Check logs or status endpoint for completion.*

---

## 5. Get Meeting Details
**Method:** `GET`
**Endpoint:** `/api/meetings/{meeting_id}`
**Description:** Retrieves the current status and summary of the meeting.

**Response:**
```json
{
  "id": 23,
  "title": "Sprint Planning Sprint 34",
  "status": "TASKS_PUSHED",
  "summary": "Team discussed payment gateway fixes and documentation updates.",
  ...
}
```

---

## 6. Get Extracted Items
**Method:** `GET`
**Endpoint:** `/api/meetings/{meeting_id}/items`
**Description:** Returns the raw items extracted by the AI (Decisions and Blockers).

**Response:**
```json
{
  "decisions": [
    "Prioritize payment bug over new features"
  ],
  "blockers": [],
  "action_items": []
}
```

---

## 7. Get Created Tasks
**Method:** `GET`
**Endpoint:** `/api/meetings/{meeting_id}/tasks`
**Description:** Returns the list of tasks that were successfully created in the external tool (Jira).

**Response:**
```json
[
  {
    "id": 15,
    "meeting_id": 23,
    "tool_type": "JIRA",
    "external_key_or_id": "KAN-12",
    "title": "Fix the payment gateway bug",
    "status": "NEW"
  },
  {
    "id": 16,
    "meeting_id": 23,
    "tool_type": "JIRA",
    "external_key_or_id": "KAN-13",
    "title": "Update documentation for API",
    "status": "NEW"
  }
]
```
