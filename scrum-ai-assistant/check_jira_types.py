
import sys
import json
from app.integrations.jira import JiraIntegrationService

def check_issue_types():
    print("🔄 Checking Issue Types for project 'KAN'...")
    try:
        jira = JiraIntegrationService()
        
        # Get Create Metadata for Project KAN
        # Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-createmeta-get
        endpoint = "/issue/createmeta?projectKeys=KAN&expand=projects.issuetypes.fields"
        
        meta = jira._make_request("GET", endpoint)
        
        if meta and meta.get('projects'):
            project = meta['projects'][0]
            print(f"✅ Project Found: {project['name']} (Key: {project['key']})")
            print("📋 Available Issue Types:")
            
            for issue_type in project['issuetypes']:
                print(f"   - {issue_type['name']} (ID: {issue_type['id']})")
                
                # Check required fields
                if 'fields' in issue_type:
                    required = [f for f, v in issue_type['fields'].items() if v.get('required')]
                    print(f"     Required fields: {', '.join(required)}")
        else:
            print("❌ Project 'KAN' not found or no create metadata returned.")

    except Exception as e:
        print(f"❌ Error checking issue types: {str(e)}")

if __name__ == "__main__":
    check_issue_types()
