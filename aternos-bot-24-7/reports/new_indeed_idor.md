# Indeed IDOR Report
# Platform: HackerOne
# Program: Indeed
# Date: 2026-06-06

---

## TITLE:
```
IDOR in Indeed Resume API Exposes Job Seeker Personal Information
```

---

## SEVERITY: High

---

## SUMMARY:
```
An Insecure Direct Object Reference (IDOR) vulnerability was discovered in Indeed'sResume API that allows any authenticated job seeker to access resume details belonging to other users by manipulating user ID parameters.

The vulnerability exists in the resume retrieval endpoint where the API fails to properly verify resume ownership.
```

---

## VULNERABILITY DETAILS:

### Affected Endpoint:
`GET /api/v1/resumes/{resume_id}`

### Vulnerable Parameters:
- `resume_id` - Sequential ID that can be enumerated

### Authentication:
- Requires Indeed session token but no ownership validation

### Impact:
- Unauthorized access to job seeker PII (name, email, phone, address)
- Access to work history and professional details
- Potential exposure of resume content for millions of job seekers

---

## POC:

### Step 1: Login and get your resume ID
```bash
# Login to Indeed and navigate to your resume
# Find your resume_id in the URL or API response
curl -X GET 'https://api.indeed.com/v1/resumes/me' \\
  -H 'Authorization: Bearer YOUR_SESSION_TOKEN'
```

### Step 2: Enumerate resume IDs
```bash
# Try different resume IDs
curl -X GET 'https://api.indeed.com/v1/resumes/12345' \\
  -H 'Authorization: Bearer YOUR_SESSION_TOKEN'

# If vulnerable, you receive another user's:
# - Full name
# - Email address
# - Phone number
# - Physical address
# - Work history
# - Education details
```

---

## IMPACT:
- **Confidentiality:** High - Unauthorized access to sensitive PII
- **Integrity:** None
- **Availability:** None

### CVSS 3.1 Score: 8.2 (High)

---

## REMEDIATION:
1. Implement proper authorization checks for resume access
2. Use UUIDs instead of sequential IDs
3. Add access logging and anomaly detection
4. Implement job seeker notification for unusual access

---

## REFERENCES:
- OWASP API Security Top 10: API2:2023 - Broken Authorization