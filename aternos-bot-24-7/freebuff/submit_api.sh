#!/bin/bash
#
# HackerOne API Report Submitter using curl
# Usage: ./submit_api.sh <report_file.md> <program_slug>
#
# Environment Variables Required:
#   H1_API_IDENTIFIER - Your HackerOne API Identifier
#   H1_API_TOKEN - Your HackerOne API Token
#

set -e

# Configuration
H1_API_BASE="https://api.hackerone.com/v1"
REPORTS_DIR="$(dirname "$0")/../reports"

# Colors
RED='\n\n\n❌ '
GREEN='\n\n\n✅ '
YELLOW='\n\n\n⚠️  '

# Check credentials
check_credentials() {
    if [[ -z "$H1_API_IDENTIFIER" || -z "$H1_API_TOKEN" ]]; then
        echo -e "${YELLOW}Missing API credentials!"
        echo ""
        echo "Set these environment variables:"
        echo "  export H1_API_IDENTIFIER=\"your_identifier\""
        echo "  export H1_API_TOKEN=\"your_token\""
        echo ""
        echo "Get your API credentials from: https://hackerone.com/settings/authentication/api"
        exit 1
    fi
}

# Submit report via API
submit_report() {
    local report_file="$1"
    local program_slug="$2"
    
    if [[ ! -f "$report_file" ]]; then
        echo -e "${RED}Report file not found: $report_file"
        exit 1
    fi
    
    # Read report content
    local content=$(cat "$report_file")
    
    # Extract title (first # heading)
    local title=$(echo "$content" | grep -m1 "^# " | sed 's/^# //')
    
    # Extract severity
    local severity=$(echo "$content" | grep -i "severity" | grep ":" | head -1 | sed 's/.*://' | tr -d ' *-')
    severity=${severity:-medium}
    
    # Extract description (everything after Summary)
    local description=$(echo "$content" | awk '/## Summary/,/## / {if(/## / && !/## Summary/) exit; print}' | tail -n +2 | head -100)
    
    # Create JSON payload safely using jq (prevents injection)
    local payload=$(jq -n \
      --arg slug "$program_slug" \
      --arg t "$title" \
      --arg desc "$description" \
      --arg sev "$severity" \
      '{
        data: {
          type: "report",
          attributes: {
            team_handle: $slug,
            title: $t,
            vulnerability_information: $desc,
            severity_rating: $sev
          }
        }
      }')
    
    echo -e "${YELLOW}Submitting report..."
    echo "  Program: $program_slug"
    echo "  Title: $title"
    echo "  Severity: $severity"
    
    # Make API request
    local auth=$(echo -n "$H1_API_IDENTIFIER:$H1_API_TOKEN" | base64)
    local response=$(curl -s -w "\n%{http_code}" -X POST "${H1_API_BASE}/hackers/reports" -H "Authorization: Basic ${auth}" -H "Content-Type: application/json" -d "${payload}")
    
    local http_code=$(echo "$response" | tail -1)
    local body=$(echo "$response" | head -n -1)
    
    if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
        echo -e "${GREEN}Report submitted successfully!"
        echo "$body" | jq -r '.data.id // "unknown"' 2>/dev/null && echo "Report ID extracted"
        return 0
    else
        echo -e "${RED}Failed with HTTP $http_code"
        echo "$body"
        return 1
    fi
}

# List available reports
list_reports() {
    echo "Available reports in $REPORTS_DIR:"
    echo ""
    ls -1 "$REPORTS_DIR"/new_*.md 2>/dev/null | head -20
    echo ""
    echo "Total CORS reports: $(ls -1 "$REPORTS_DIR"/new_*_cors*.md 2>/dev/null | wc -l)"
    echo "Total SSRF reports: $(ls -1 "$REPORTS_DIR"/new_*_ssrf*.md 2>/dev/null | wc -l)"
    echo "Total IDOR reports: $(ls -1 "$REPORTS_DIR"/new_*_idor*.md 2>/dev/null | wc -l)"
}

# Main
main() {
    case "${1:-}" in
        submit)
            check_credentials
            submit_report "$2" "$3"
            ;;
        list)
            list_reports
            ;;
        help|--help|-h)
            echo "HackerOne API Report Submitter"
            echo ""
            echo "Usage:"
            echo "  $0 list                              - List available reports"
            echo "  $0 submit <file.md> <program_slug>   - Submit a report"
            echo ""
            echo "Examples:"
            echo "  $0 list"
            echo "  $0 submit reports/new_github_cors.md github"
            echo "  $0 submit reports/new_stripe_cors.md stripe"
            echo ""
            echo "Required environment variables:"
            echo "  export H1_API_IDENTIFIER=\"your_id\""
            echo "  export H1_API_TOKEN=\"your_token\""
            ;;
        *)
            echo "Unknown command: ${1:-}"
            echo "Run '$0 help' for usage"
            exit 1
            ;;
    esac
}

main "$@"