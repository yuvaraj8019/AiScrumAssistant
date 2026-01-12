
import sys
import json
from app.integrations.jira import JiraIntegrationService

def test_jira():
    print("🔄 Testing Jira Connection...")
    try:
        jira = JiraIntegrationService()
        
        print(f"📡 Connecting to: {jira.base_url}")
        print(f"📧 User: {jira.user_email}")
        
        # 1. Test Project List (GET /project)
        print("\n📂 Fetching visible projects...")
        try:
            projects = jira._make_request("GET", "/project")
            if projects:
                print(f"✅ Found {len(projects)} projects:")
                for p in projects:
                    print(f"   - {p.get('name')} (Key: {p.get('key')})")
            else:
                print("⚠️  Authenticated, but no projects found.")
                
        except Exception as e:
            print(f"❌ Failed to list projects: {str(e)}")
            return

        # 2. Test Create Issue Metadata (to check if we can create tasks)
        # This checks if we have permission to create issues in the first project found
        if projects:
            first_project_key = projects[0].get('key')
            print(f"\n📝 Checking create permissions for project '{first_project_key}'...")
            try:
                # Just checking if we can get metadata for creating issues
                meta = jira._make_request("GET", f"/issue/createmeta?projectKeys={first_project_key}&expand=projects.issuetypes.fields")
                if meta and meta.get('projects'):
                     print(f"✅ Can access issue metadata for {first_project_key}")
                     print("🎉 Jira is FULLY CONNECTED and READY!")
                else:
                     print("⚠️  Could not get create metadata (might be permissions issue)")

            except Exception as e:
                print(f"❌ Failed to check create permissions: {str(e)}")

    except Exception as e:
        print(f"❌ Failed to initialize Jira service: {str(e)}")

if __name__ == "__main__":
    test_jira()
