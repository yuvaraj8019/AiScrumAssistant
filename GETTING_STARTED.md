# 🚀 Beginner's Quick Start - 3 Easy Steps

## For People New to Python

Welcome! This guide is designed for complete beginners. **You don't need to know Python to run this project.**

---

## 📋 What You Need

✅ Computer with:
- Docker Desktop (free software)
- Terminal/Command Line
- Web browser
- ~5 minutes of time

That's it! No need to install Python, databases, etc.

---

## ⚡ 3 Easy Steps to Get Started

### **Step 1: Start the Application (1 minute)**

Open your terminal and run:

```bash
cd /workspaces/AiScrumAssistant/scrum-ai-assistant

docker-compose up -d
```

**What's happening?**
- Docker is downloading and starting 5 services
- This includes: database, web server, job processor, and scheduler
- The `-d` means "run in background"

**Wait 30 seconds** ⏳

### **Step 2: Initialize Database (1 minute)**

```bash
docker-compose exec api alembic upgrade head
```

**What's happening?**
- Creating the database tables
- This only needs to run once

### **Step 3: Verify It Works (1 minute)**

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"healthy","service":"Scrum AI Assistant","version":"1.0.0"}
```

✅ **Done!** Your app is running!

---

## 🧪 Test the Application

### Option A: Easy - Use Interactive Web Interface

**Best for beginners!**

1. Open your web browser
2. Go to: `http://localhost:8000/docs`
3. You'll see an interactive API explorer
4. Click on any endpoint and click "Try it out"

### Option B: Run Automated Test Script

```bash
# Make sure you're in the project folder
cd /workspaces/AiScrumAssistant/scrum-ai-assistant

# Run the test script
bash test-api.sh
```

This will:
- ✅ Create a meeting
- ✅ Add a transcript
- ✅ Process it with AI
- ✅ Show extracted data
- ✅ Display created tasks

**Should take 10 seconds and show results!**

### Option C: Manual Testing with Commands

If you want to see each step:

```bash
# 1. Create a meeting
curl -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Meeting",
    "ceremony_type": "STANDUP",
    "meeting_date": "2024-01-10T09:00:00",
    "tool_type": "JIRA",
    "project_key": "TEST"
  }'

# Note the "id" value in the response (e.g., "id": 1)
# Use that ID in the commands below
```

```bash
# 2. Add a transcript (replace MEETING_ID with the id from above)
curl -X POST http://localhost:8000/api/meetings/MEETING_ID/transcript \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Meeting about sprint planning tasks"}'
```

```bash
# 3. Process the meeting
curl -X POST http://localhost:8000/api/meetings/MEETING_ID/process
```

```bash
# 4. View extracted data
curl http://localhost:8000/api/meetings/MEETING_ID/items
```

```bash
# 5. View created tasks
curl http://localhost:8000/api/meetings/MEETING_ID/tasks
```

---

## 📊 Understanding What You're Testing

### What is the API?
- An API is like a waiter in a restaurant
- You (the client) ask the API for something (order)
- The API talks to the database and returns information (brings food)

### The Test Does This:

```
1. Create Meeting   → Saves meeting info to database
2. Add Transcript   → Stores the meeting transcript
3. Process Meeting  → AI reads transcript and extracts:
                      - Decisions made
                      - Blockers/problems
                      - Action items/tasks
4. View Results     → Shows what was extracted
```

### What You Should See:

```
"decisions": [
  "Use React Query for data fetching",
  "Schedule database migration"
],
"blockers": [
  {
    "description": "API endpoint not ready",
    "owner": "John"
  }
],
"action_items": [
  {
    "title": "Complete payment integration",
    "assignee": "Tom",
    "due_date": "2024-01-12"
  }
]
```

---

## 🔧 Common Commands

### View What's Happening (Logs)

```bash
# See API logs in real-time
docker-compose logs -f api

# See background job logs
docker-compose logs -f celery_worker

# Press Ctrl+C to stop viewing
```

### Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove data (CAREFUL!)
docker-compose down -v
```

### Restart the Application

```bash
# Stop everything
docker-compose down

# Start everything again
docker-compose up -d

# Reinitialize database
docker-compose exec api alembic upgrade head
```

### Check Service Status

```bash
# See which services are running
docker-compose ps

# Check if database is healthy
docker-compose exec postgres pg_isready -U postgres

# Check if Redis is healthy
docker-compose exec redis redis-cli ping
```

---

## ❓ Troubleshooting

### Problem: "Connection refused"

```
Error: Connection refused at localhost:8000
```

**Solution:**
- Services haven't started yet
- Wait 60 seconds and try again
- Check status: `docker-compose ps`

### Problem: "Cannot find database"

```
Error: database "scrum_db" does not exist
```

**Solution:**
```bash
# Run migrations again
docker-compose exec api alembic upgrade head
```

### Problem: "Port 8000 already in use"

```
Error: bind: address already in use
```

**Solution:**
```bash
# Find and kill the process using port 8000
# Or restart Docker
docker-compose down
docker-compose up -d
```

### Problem: Docker command not found

```
Error: command not found: docker
```

**Solution:**
- Install Docker Desktop from https://www.docker.com/products/docker-desktop
- Restart your terminal after installing

### Problem: "jq command not found" (for pretty JSON output)

```bash
# Don't use jq, just use curl
curl http://localhost:8000/api/meetings
# Output won't be pretty, but will work
```

---

## 📚 Learn More

### Start with These Files (in order):

1. **BEGINNER_GUIDE.md** (detailed explanations)
2. **QUICKSTART.md** (5-minute overview)
3. **README.md** (all features)
4. **ARCHITECTURE.md** (how it all works)

### Interactive Learning:

1. Visit http://localhost:8000/docs
2. Expand each endpoint
3. Click "Try it out"
4. Change the data and see what happens

---

## 🎯 What You Can Do Now

✅ Create meetings
✅ Add meeting transcripts
✅ Extract decisions and blockers
✅ Create tasks in Jira (with credentials)
✅ Get daily follow-up notifications
✅ View all your meetings and tasks

## 🚀 Next Steps

### This Week:
- [ ] Run test-api.sh and understand the output
- [ ] Visit http://localhost:8000/docs and try endpoints
- [ ] Read BEGINNER_GUIDE.md for detailed explanations
- [ ] Try modifying transcript text to see different results

### Next Week:
- [ ] Read README.md (full features)
- [ ] Configure Jira credentials in .env file
- [ ] Set up Slack notifications
- [ ] Deploy to a server

---

## 💡 Tips for Success

1. **Take your time** - Understanding each step is more important than speed
2. **Experiment** - Try changing the meeting title, transcript, etc.
3. **Read error messages** - They usually tell you exactly what's wrong
4. **Use the web interface** - http://localhost:8000/docs is friendlier than command line
5. **Watch logs** - `docker-compose logs -f api` shows you what's happening
6. **Ask for help** - All documentation is in the project folder

---

## 🎓 Learning Path

```
Beginner                Middle              Advanced
│                       │                   │
├─ Run the app          ├─ Modify config    ├─ Deploy to cloud
├─ Test endpoints       ├─ Add credentials  ├─ Scale services
├─ View docs            ├─ Send to Slack    ├─ Monitor production
└─ Understand flow      └─ Read code        └─ Optimize performance
```

---

## ✨ You're Ready!

Congratulations! 🎉

You now know:
- ✅ How to run a Python application with Docker
- ✅ How to test an API
- ✅ How to read responses
- ✅ How to troubleshoot issues

**You don't need to write any Python code to use this app!**

---

## 📞 Quick Reference

```bash
# Start services
docker-compose up -d

# Initialize database
docker-compose exec api alembic upgrade head

# Run tests
bash test-api.sh

# View API documentation
# Open: http://localhost:8000/docs

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# View service status
docker-compose ps
```

---

## 🎉 That's It!

You're all set to automate your Scrum meetings!

**Questions?** Check out the documentation files in the project folder.

Happy automating! 🚀
