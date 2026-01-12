# API Testing Guide

This guide provides example JSON payloads for testing the Scrum AI Assistant APIs via Swagger UI (`http://localhost:8000/docs`) or `curl`.

## 1. Create Meeting
**Endpoint:** `POST /api/meetings/`

Initialize a new meeting record.

```json
{
  "title": "Daily Scrum",
  "ceremony_type": "DAILY_STANDUP",
  "meeting_date": "2024-01-13T10:00:00",
  "tool_type": "JIRA",
  "project_key": "KAN"
}
```

*   **ceremony_type**: `DAILY_STANDUP`, `PLANNING`, `RETROSPECTIVE`, `REVIEW`
*   **tool_type**: `JIRA` (Azure/Trello planned)
*   **project_key**: Valid project key from your Jira instance

---

## 2. Add Transcript
**Endpoint:** `POST /api/meetings/{meeting_id}/transcript`

Add text transcript directly (skipping audio upload).

```json
{
  "transcript": "Hello team. Today we need to fix the login bug. It's a critical blocker for the release. Sarah, please investigate the auth service logs. John, continue with the dashboard frontend. We plan to deploy by Friday."
}
```

---

## 3. Upload Audio
**Endpoint:** `POST /api/meetings/{meeting_id}/upload`

*   **Format**: `multipart/form-data`
*   **Input**: `file` (Select .mp3, .wav, .m4a)

---

## 4. Process Meeting
**Endpoint:** `POST /api/meetings/{meeting_id}/process`

Triggers AI analysis and Jira task creation.

*   **Payload**: `None` (Empty body)
*   **Action**: Extracts decisions, blockers, and action items; creates tasks in Jira.

---

## 5. Get Results
**Endpoint:** `GET /api/meetings/{meeting_id}`
*   Returns status and summary.

**Endpoint:** `GET /api/meetings/{meeting_id}/items`
*   Returns extracted Decisions and Blockers.

**Endpoint:** `GET /api/meetings/{meeting_id}/tasks`
*   Returns created Jira tasks (e.g., `KAN-15`).
