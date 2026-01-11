# Scrum AI Assistant - Beginner's Guide for Python Users

## 📚 What You Need to Know First

### What is Python?
Python is a programming language (think of it like English for computers). The Scrum AI Assistant is written in Python. You don't need to write Python code to run it - just need to execute it.

### What is Docker?
Docker lets you package an entire application with all its dependencies into a "container" - think of it as a sealed box that contains everything the app needs to run. No need to install Python, databases, etc. on your computer separately.

### What is FastAPI?
A framework for building web applications (APIs) in Python. The Scrum AI Assistant has a web API that listens for requests at `http://localhost:8000`.

---

## ✅ Prerequisites Checklist

Before starting, make sure you have:

- [ ] Docker and Docker Compose installed
- [ ] Git (to manage code)
- [ ] A terminal/command line
- [ ] About 5 minutes for setup
- [ ] Internet connection (to download Docker images)

### How to Check if Docker is Installed

Open a terminal and run:
```bash
docker --version
docker-compose --version
```

If both show version numbers, you're good! If not, install Docker from https://www.docker.com/products/docker-desktop

---

## 🚀 Step-by-Step: Run the Project

### Step 1: Open Terminal and Navigate to Project

```bash
# Open terminal/command line
# Navigate to the project folder
cd /workspaces/AiScrumAssistant/scrum-ai-assistant

# Verify you're in the right place
ls
# You should see: Dockerfile, README.md, docker-compose.yml, app/, etc.
```

**What's happening?**
- `cd` = "change directory" (move to a different folder)
- `ls` = "list files" (show what's in this folder)

### Step 2: Create Environment Configuration File

```bash
# Copy the example environment file
cp .env.example .env

# This creates a `.env` file with default settings
# .env is like a settings file for the application
```

**What's happening?**
- `.env` = a file containing configuration (like settings)
- This file tells the app how to connect to databases, APIs, etc.

### Step 3: Start All Services

```bash
# This command starts everything:
# - PostgreSQL (database)
# - Redis (cache/message storage)
# - FastAPI (web server)
# - Celery Worker (background jobs)
# - Celery Beat (scheduler)

docker-compose up -d
```

**What does `-d` mean?**
- `-d` = "detached" (run in background, don't show logs by default)

**Wait a moment (30-60 seconds) for services to start**

### Step 4: Initialize the Database

```bash
# This creates the database tables
docker-compose exec api alembic upgrade head
```

**What's happening?**
- `docker-compose exec` = "run a command inside a Docker container"
- `api` = which container to run it in
- `alembic upgrade head` = database initialization command

### Step 5: Verify Everything Works

```bash
# Check if API is responding
curl http://localhost:8000/health

# You should see:
# {"status":"healthy","service":"Scrum AI Assistant","version":"1.0.0"}
```

**Congratulations! 🎉 The app is running!**

---

## 🧪 Testing the API (Beginner-Friendly)

### Method 1: Using Web Browser (Easiest)

Simply open your browser and go to:
```
http://localhost:8000/docs
```

**What you'll see:**
- Interactive API documentation
- All available endpoints (API functions)
- A "Try it out" button to test each endpoint

### Method 2: Using cURL (Command Line)

cURL is a command-line tool to make HTTP requests. Here's a complete test:

#### Test 1: Create a Meeting

```bash
curl -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "ceremony_type": "STANDUP",
    "meeting_date": "2024-01-10T09:00:00",
    "tool_type": "JIRA",
    "project_key": "TEST"
  }'
```

**What's happening?**
- `curl` = command to make web requests
- `-X POST` = type of request (CREATE)
- `-H` = header (tells server: "I'm sending JSON")
- `-d` = data (the JSON information)

**Expected Response:**
```json
{
  "id": 1,
  "title": "Daily Standup",
  "status": "CREATED",
  "ceremony_type": "STANDUP",
  ...
}
```

**Note the `"id": 1`** - you'll need this for next steps!

#### Test 2: Add Meeting Transcript

```bash
# Add a transcript (replace MEETING_ID with the id from Test 1, e.g., 1)
curl -X POST http://localhost:8000/api/meetings/MEETING_ID/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Good morning team. Sarah finished the login feature. Decision: Use React Query. John is blocked on API endpoint. Action item: Tom complete payment integration by Friday."
  }'
```

**Expected Response:**
```json
{"message": "Transcript added successfully"}
```

#### Test 3: Process the Meeting (Async Job)

```bash
curl -X POST http://localhost:8000/api/meetings/MEETING_ID/process
```

**Expected Response:**
```json
{"started": true, "meeting_id": 1}
```

**Wait 3-5 seconds** for background processing

#### Test 4: Get Extracted Items

```bash
curl http://localhost:8000/api/meetings/MEETING_ID/items
```

**Expected Response:**
```json
{
  "decisions": [
    "Use React Query for data fetching"
  ],
  "blockers": [
    {
      "description": "API endpoint for user profile not ready",
      "owner": "John"
    }
  ]
}
```

#### Test 5: Get Created Tasks

```bash
curl http://localhost:8000/api/meetings/MEETING_ID/tasks
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "meeting_id": 1,
    "tool_type": "JIRA",
    "external_key_or_id": "TEST-123",
    "title": "Complete payment gateway integration",
    "status": "PUSHED"
  }
]
```

---

## 🐍 Complete Test Script (Easiest for Beginners)

Save this as a `.sh` file and run it:

```bash
# 1. Create a file called test-api.sh
# 2. Copy the code below into it
# 3. Run: bash test-api.sh
```

**File: test-api.sh**
```bash
#!/bin/bash

echo "🚀 Testing Scrum AI Assistant API"
echo "=================================="

# Test 1: Health Check
echo ""
echo "1️⃣  Testing health endpoint..."
curl -s http://localhost:8000/health | jq .
echo ""

# Test 2: Create Meeting
echo "2️⃣  Creating a meeting..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting",
    "ceremony_type": "STANDUP",
    "meeting_date": "2024-01-10T09:00:00",
    "tool_type": "JIRA",
    "project_key": "TEST"
  }')

echo "$RESPONSE" | jq .
MEETING_ID=$(echo "$RESPONSE" | jq -r '.id')
echo "Created meeting with ID: $MEETING_ID"
echo ""

# Test 3: Add Transcript
echo "3️⃣  Adding transcript..."
curl -s -X POST http://localhost:8000/api/meetings/$MEETING_ID/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Team meeting discussing sprint goals and tasks"
  }' | jq .
echo ""

# Test 4: Process Meeting
echo "4️⃣  Processing meeting (async)..."
curl -s -X POST http://localhost:8000/api/meetings/$MEETING_ID/process | jq .
echo ""

# Wait for processing
echo "⏳ Waiting for processing..."
sleep 3

# Test 5: Get Extracted Items
echo "5️⃣  Getting extracted items..."
curl -s http://localhost:8000/api/meetings/$MEETING_ID/items | jq .
echo ""

# Test 6: Get Created Tasks
echo "6️⃣  Getting created tasks..."
curl -s http://localhost:8000/api/meetings/$MEETING_ID/tasks | jq .
echo ""

echo "✅ Testing complete!"
```

**To run this:**
```bash
# Make it executable
chmod +x test-api.sh

# Run it
bash test-api.sh
```

---

## 📊 Understanding the Response (JSON)

API responses are in JSON format. Here's what it means:

```json
{
  "id": 1,
  "title": "Daily Standup",
  "status": "CREATED",
  "ceremony_type": "STANDUP"
}
```

**Breaking it down:**
- `{` `}` = container for data (dictionary/object)
- `"id"` = name of field
- `:` = "equals"
- `1` = value (a number)
- `"title": "Daily Standup"` = a text field with value

---

## 🔍 Viewing Logs (See What's Happening)

### View API Logs
```bash
# Shows logs from the API server
docker-compose logs -f api
```

### View Worker Logs
```bash
# Shows logs from background jobs
docker-compose logs -f celery_worker
```

### View All Logs
```bash
# Shows logs from everything
docker-compose logs -f
```

**Press `Ctrl+C` to stop viewing logs**

---

## 🛑 Stopping & Restarting

### Stop Everything
```bash
docker-compose down
```

### Restart Everything
```bash
docker-compose down
docker-compose up -d
docker-compose exec api alembic upgrade head
```

### Remove Everything (Careful! Deletes data!)
```bash
docker-compose down -v
# The -v removes volumes (database data is deleted)
```

---

## 🐛 Common Issues & Solutions

### Issue: "Connection refused" error

```bash
# Problem: Services not running yet
# Solution: Wait 30 seconds and try again
docker-compose logs
# Check if all services say "healthy"
```

### Issue: "Cannot find module" error

```bash
# Problem: Docker container not built properly
# Solution: Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose exec api alembic upgrade head
```

### Issue: Port 8000 already in use

```bash
# Problem: Another app is using port 8000
# Solution 1: Kill the other app
# Solution 2: Use different port - edit docker-compose.yml:
# Change "8000:8000" to "8001:8000"
```

### Issue: Database connection error

```bash
# Problem: Database not ready
# Solution: Wait longer (60 seconds) and check health
docker-compose exec postgres pg_isready -U postgres
# Should show: "accepting connections"
```

### Issue: "No such file or directory"

```bash
# Problem: Wrong directory
# Solution: Make sure you're in /workspaces/AiScrumAssistant/scrum-ai-assistant
pwd
# Should show: /workspaces/AiScrumAssistant/scrum-ai-assistant
```

---

## 📱 Testing Different Scenarios

### Scenario 1: Complete Demo Workflow

```bash
#!/bin/bash
# Complete workflow test

MEETING_ID=1

# 1. Create
echo "Creating meeting..."
curl -s -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint Planning",
    "ceremony_type": "PLANNING",
    "meeting_date": "2024-01-10T10:00:00",
    "tool_type": "JIRA",
    "project_key": "DEMO"
  }' | jq .

# 2. Add Transcript
echo "Adding transcript..."
curl -s -X POST http://localhost:8000/api/meetings/$MEETING_ID/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Sprint planning meeting. We need to complete OB-123 feature. Sarah handles UI, John handles API. Decision: Use React Query. Blocker: Schema not finalized. Action: Tom complete payment by Friday."
  }' | jq .

# 3. Process
echo "Processing..."
curl -s -X POST http://localhost:8000/api/meetings/$MEETING_ID/process | jq .

# 4. Results
echo "Waiting for processing..."
sleep 3

echo "Extracted items:"
curl -s http://localhost:8000/api/meetings/$MEETING_ID/items | jq .

echo "Created tasks:"
curl -s http://localhost:8000/api/meetings/$MEETING_ID/tasks | jq .
```

### Scenario 2: Create Multiple Meetings

```bash
for i in {1..3}; do
  echo "Creating meeting $i..."
  curl -s -X POST http://localhost:8000/api/meetings \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"Meeting $i\",
      \"ceremony_type\": \"STANDUP\",
      \"meeting_date\": \"2024-01-10T09:00:00\",
      \"tool_type\": \"JIRA\",
      \"project_key\": \"TEST\"
    }" | jq '.id'
  
  sleep 1
done
```

---

## 📖 Understanding the Project Structure

```
scrum-ai-assistant/          ← Main folder
├── app/                     ← Python application code
│   ├── main.py             ← Starts the API server
│   ├── core/               ← Database, config, logging
│   ├── models/             ← Database tables definition
│   ├── schemas/            ← Data format definition
│   ├── services/           ← Business logic
│   ├── api/routes/         ← API endpoints (REST)
│   └── integrations/       ← External connections (Jira, Slack)
├── docker-compose.yml      ← Start multiple services with one command
├── requirements.txt        ← Python packages to install
├── .env.example            ← Settings template
└── README.md               ← Full documentation
```

**You don't need to modify any of these files to run the app!**

---

## 🎓 Next: Learn More

### Read Documentation (in order)
1. **QUICKSTART.md** - 5-minute overview
2. **README.md** - Complete feature guide
3. **ARCHITECTURE.md** - How everything works

### Try Advanced Tests
```bash
# Get all meetings
curl http://localhost:8000/api/meetings | jq .

# Get specific meeting
curl http://localhost:8000/api/meetings/1 | jq .

# Upload audio (create an mp3 file first)
curl -F "file=@meeting.mp3" http://localhost:8000/api/meetings/1/upload-audio
```

### Modify Configuration
Edit `.env` file to:
- Add real Jira credentials
- Add Slack webhook URL
- Change database settings

---

## 💡 Tips for Beginners

1. **Take it slow** - Run one command at a time, understand what it does
2. **Read error messages** - They usually tell you exactly what's wrong
3. **Use `jq`** - Makes JSON output pretty and readable
4. **Watch logs** - `docker-compose logs -f` shows you what's happening in real-time
5. **Bookmark the API docs** - http://localhost:8000/docs is your best friend
6. **Test incrementally** - Test one endpoint at a time

---

## 🎉 Congratulations!

You now know how to:
- ✅ Run a Python application with Docker
- ✅ Test an API with cURL
- ✅ Read API responses
- ✅ Debug issues
- ✅ Monitor what's happening

**You don't need to write Python code to use this application - just need to know how to run it and test it!**

---

## ❓ Questions?

See full documentation:
- **For running**: QUICKSTART.md
- **For all features**: README.md
- **For system design**: ARCHITECTURE.md

Happy automating Scrum meetings! 🚀
