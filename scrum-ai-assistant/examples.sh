#!/bin/bash
# Scrum AI Assistant - API Testing Commands
# Run from project root: bash examples.sh

set -e

BASE_URL="http://localhost:8000"

echo "🚀 Scrum AI Assistant - API Examples"
echo "===================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function
call_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${BLUE}→${NC} $description"
    echo "   Command: curl -X $method $BASE_URL$endpoint"
    if [ -n "$data" ]; then
        echo "   Data: $data"
        curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" | jq . || echo "Request failed or invalid JSON"
    else
        curl -s -X "$method" "$BASE_URL$endpoint" | jq . || echo "Request failed"
    fi
    echo ""
}

# 1. Health Check
echo -e "${YELLOW}1. Health Check${NC}"
call_api "GET" "/health" "" "Check API is running"

# 2. Create Meeting
echo -e "${YELLOW}2. Create Meeting${NC}"
MEETING_RESPONSE=$(curl -s -X POST "$BASE_URL/api/meetings" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Sprint Planning Meeting",
        "ceremony_type": "PLANNING",
        "meeting_date": "2024-01-10T10:00:00",
        "tool_type": "JIRA",
        "project_key": "OB"
    }')

echo -e "${BLUE}→${NC} Create new meeting"
echo "$MEETING_RESPONSE" | jq .
MEETING_ID=$(echo "$MEETING_RESPONSE" | jq -r '.id')
echo -e "${GREEN}✓ Created meeting ID: $MEETING_ID${NC}"
echo ""

# 3. Get Meeting Details
echo -e "${YELLOW}3. Get Meeting Details${NC}"
call_api "GET" "/api/meetings/$MEETING_ID" "" "Retrieve meeting details"

# 4. Add Transcript
echo -e "${YELLOW}4. Add Meeting Transcript${NC}"
TRANSCRIPT="Good morning team. Let's discuss our sprint. We need to complete feature OB-123 by Friday. Sarah will handle the UI component, John will work on the backend API. Decision: We will use React Query for data fetching. Blocker: Database schema is still being finalized. Action item: Tom needs to complete payment gateway integration. Tom, can you confirm? Yes, I will have it done by Friday."

curl -s -X POST "$BASE_URL/api/meetings/$MEETING_ID/transcript" \
    -H "Content-Type: application/json" \
    -d "{\"transcript\": \"$TRANSCRIPT\"}" | jq .
echo ""

# 5. Process Meeting (Async)
echo -e "${YELLOW}5. Process Meeting (Async)${NC}"
call_api "POST" "/api/meetings/$MEETING_ID/process" "" "Trigger meeting processing"

# Wait for processing to complete
echo -e "${YELLOW}Waiting for processing to complete...${NC}"
sleep 3

# 6. Get Extracted Items
echo -e "${YELLOW}6. Get Extracted Items${NC}"
call_api "GET" "/api/meetings/$MEETING_ID/items" "" "Retrieve decisions and blockers"

# 7. Get Created Tasks
echo -e "${YELLOW}7. Get Created Tasks${NC}"
call_api "GET" "/api/meetings/$MEETING_ID/tasks" "" "Retrieve created tasks"

# 8. List All Meetings
echo -e "${YELLOW}8. List All Meetings${NC}"
call_api "GET" "/api/meetings?skip=0&limit=10" "" "List meetings with pagination"

echo -e "${GREEN}✅ All examples completed!${NC}"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
