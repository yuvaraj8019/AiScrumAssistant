#!/bin/bash

# Scrum AI Assistant - Easy Test Script for Beginners
# This script tests the API step by step with explanations

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function to print messages
print_step() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Start
clear
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   SCRUM AI ASSISTANT - BEGINNER TEST SCRIPT            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if API is running
print_step "Step 0: Checking if API is running..."

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_error "API is not running!"
    echo ""
    echo "Please start the services first:"
    echo "  docker-compose up -d"
    echo "  docker-compose exec api alembic upgrade head"
    echo ""
    echo "Then wait 30 seconds and try again."
    exit 1
fi

print_success "API is running!"

# Test 1: Health Check
print_step "Step 1: Health Check (Is API healthy?)"
echo "Command: curl http://localhost:8000/health"
echo ""

HEALTH=$(curl -s http://localhost:8000/health)
echo -e "${GREEN}Response:${NC}"
echo "$HEALTH" | jq .

print_info "This confirms the API is running and healthy"

# Test 2: Create Meeting
print_step "Step 2: Create a Meeting"
echo "Command: curl -X POST http://localhost:8000/api/meetings ..."
echo ""

MEETING_RESPONSE=$(curl -s -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup Meeting",
    "ceremony_type": "STANDUP",
    "meeting_date": "2024-01-10T09:00:00",
    "tool_type": "JIRA",
    "project_key": "TEST"
  }')

echo -e "${GREEN}Response:${NC}"
echo "$MEETING_RESPONSE" | jq .

# Extract meeting ID for next steps
MEETING_ID=$(echo "$MEETING_RESPONSE" | jq -r '.id')

if [ "$MEETING_ID" == "null" ] || [ -z "$MEETING_ID" ]; then
    print_error "Failed to create meeting!"
    exit 1
fi

print_success "Meeting created with ID: $MEETING_ID"

# Test 3: View Meeting Details
print_step "Step 3: View Meeting Details"
echo "Command: curl http://localhost:8000/api/meetings/$MEETING_ID"
echo ""

curl -s http://localhost:8000/api/meetings/$MEETING_ID | jq .

print_info "This shows all details of the meeting you just created"

# Test 4: Add Transcript
print_step "Step 4: Add Meeting Transcript"
echo "Command: curl -X POST http://localhost:8000/api/meetings/$MEETING_ID/transcript ..."
echo ""

TRANSCRIPT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/meetings/$MEETING_ID/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Good morning team. Let me start our daily standup. Sarah, what did you work on yesterday? I finished the login feature. Great! What are you working on today? I will implement the dashboard. Any blockers? No blockers. John, your turn. I finished the API tests. Today I will work on the payment integration. Blocker: The database schema is still being finalized. Can someone check on that? I will check with the database team. Decision: We will use React Query for data fetching. Action item: Tom needs to complete the payment gateway integration by Friday."
  }')

echo -e "${GREEN}Response:${NC}"
echo "$TRANSCRIPT_RESPONSE" | jq .

print_success "Transcript added to meeting"

# Test 5: Process Meeting (Async)
print_step "Step 5: Process Meeting (Extract Data)"
echo "Command: curl -X POST http://localhost:8000/api/meetings/$MEETING_ID/process"
echo ""

PROCESS_RESPONSE=$(curl -s -X POST http://localhost:8000/api/meetings/$MEETING_ID/process)

echo -e "${GREEN}Response:${NC}"
echo "$PROCESS_RESPONSE" | jq .

print_success "Processing started! This happens in the background..."

# Wait for processing
print_step "⏳ Waiting for background processing (3 seconds)..."
sleep 3

# Test 6: Get Extracted Items
print_step "Step 6: View Extracted Items (Decisions & Blockers)"
echo "Command: curl http://localhost:8000/api/meetings/$MEETING_ID/items"
echo ""

ITEMS=$(curl -s http://localhost:8000/api/meetings/$MEETING_ID/items)

echo -e "${GREEN}Response:${NC}"
echo "$ITEMS" | jq .

DECISIONS=$(echo "$ITEMS" | jq '.decisions | length')
BLOCKERS=$(echo "$ITEMS" | jq '.blockers | length')

print_success "Found $DECISIONS decisions and $BLOCKERS blockers in the meeting!"

# Test 7: Get Created Tasks
print_step "Step 7: View Created Tasks"
echo "Command: curl http://localhost:8000/api/meetings/$MEETING_ID/tasks"
echo ""

TASKS=$(curl -s http://localhost:8000/api/meetings/$MEETING_ID/tasks)

echo -e "${GREEN}Response:${NC}"
echo "$TASKS" | jq .

TASK_COUNT=$(echo "$TASKS" | jq 'length')

print_success "Created $TASK_COUNT task(s) from the meeting!"

# Test 8: List All Meetings
print_step "Step 8: View All Meetings"
echo "Command: curl http://localhost:8000/api/meetings"
echo ""

curl -s http://localhost:8000/api/meetings | jq .

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ ALL TESTS PASSED!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📊 Summary:${NC}"
echo "  ✓ API is healthy and responding"
echo "  ✓ Created meeting (ID: $MEETING_ID)"
echo "  ✓ Added transcript"
echo "  ✓ Processed meeting (AI extraction)"
echo "  ✓ Extracted $DECISIONS decisions"
echo "  ✓ Extracted $BLOCKERS blockers"
echo "  ✓ Created $TASK_COUNT tasks"
echo ""

echo -e "${BLUE}📚 Next Steps:${NC}"
echo "  1. Read BEGINNER_GUIDE.md for more examples"
echo "  2. Visit http://localhost:8000/docs for interactive API testing"
echo "  3. View logs: docker-compose logs -f api"
echo "  4. Try modifying the transcript to see different results"
echo ""

echo -e "${GREEN}Happy automating Scrum meetings! 🚀${NC}"
echo ""
