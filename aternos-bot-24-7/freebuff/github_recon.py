#!/usr/bin/env python3
"""
SARAhack - GitHub Reconnaissance Script
วิเคราะห์ GitHub repos สำหรับ Bug Bounty

Usage:
    python3 github_recon.py --org github --search "org:github filename:config"
    python3 github_recon.py --user potsopotosolo
    python3 github_recon.py --dorks "aws api key language:python"
"""

import os
import sys
import argparse
import requests
import json
from urllib.parse import quote_plus

# GitHub Token from environment
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# API Configuration
BASE_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def search_code(query, per_page=30):
    """ค้นหา code บน GitHub"""
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set in environment")
        return []
    
    url = f"{BASE_URL}/search/code"
    params = {
        "q": query,
        "per_page": per_page,
        "page": 1
    }
    
    print(f"[*] Searching: {query}")
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[+] Found {data.get('total_count', 0)} results")
        return data.get('items', [])
    elif response.status_code == 401:
        print("[ERROR] Invalid or expired GitHub token")
    elif response.status_code == 403:
        print("[ERROR] Rate limit exceeded. Use authenticated token.")
    else:
        print(f"[ERROR] API request failed: {response.status_code}")
    
    return []

def search_repos(query, per_page=30):
    """ค้นหา repos บน GitHub"""
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set in environment")
        return []
    
    url = f"{BASE_URL}/search/repositories"
    params = {
        "q": query,
        "per_page": per_page,
        "sort": "stars",
        "order": "desc"
    }
    
    print(f"[*] Searching repos: {query}")
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[+] Found {data.get('total_count', 0)} repos")
        return data.get('items', [])
    
    return []

def get_user_info(username):
    """ดึงข้อมูล user"""
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set in environment")
        return None
    
    url = f"{BASE_URL}/users/{username}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    
    print(f"[ERROR] User not found: {username}")
    return None

def get_org_info(org):
    """ดึงข้อมูล organization"""
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set in environment")
        return None
    
    url = f"{BASE_URL}/orgs/{org}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    
    print(f"[ERROR] Organization not found: {org}")
    return None

def list_user_repos(username, per_page=100):
    """List all repos ของ user"""
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set in environment")
        return []
    
    repos = []
    page = 1
    
    while len(repos) < per_page:
        url = f"{BASE_URL}/users/{username}/repos"
        params = {"per_page": 100, "page": page, "type": "all"}
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            break
        
        data = response.json()
        if not data:
            break
        
        repos.extend(data)
        page += 1
        
        # Check rate limit
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        if remaining < 5:
            print("[!] Rate limit low, stopping...")
            break
    
    return repos[:per_page]

def list_org_repos(org, per_page=100):
    """List all repos ของ organization"""
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set in environment")
        return []
    
    repos = []
    page = 1
    
    while len(repos) < per_page:
        url = f"{BASE_URL}/orgs/{org}/repos"
        params = {"per_page": 100, "page": page}
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            break
        
        data = response.json()
        if not data:
            break
        
        repos.extend(data)
        page += 1
        
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        if remaining < 5:
            print("[!] Rate limit low, stopping...")
            break
    
    return repos[:per_page]

def check_rate_limit():
    """เช็ค rate limit ที่เหลือ"""
    url = f"{BASE_URL}/rate_limit"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        core = data.get('resources', {}).get('core', {})
        remaining = core.get('remaining', 0)
        limit = core.get('limit', 0)
        reset_time = core.get('reset', 0)
        
        print(f"[*] Rate limit: {remaining}/{limit}")
        print(f"[*] Resets at: {reset_time}")
        return remaining
    
    return 0

def main():
    parser = argparse.ArgumentParser(description="SARAhack - GitHub Recon")
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--org", help="Organization to analyze")
    parser.add_argument("--user", help="User to analyze")
    parser.add_argument("--search", help="Search code on GitHub")
    parser.add_argument("--repos", help="Search repositories")
    parser.add_argument("--dorks", help="GitHub dorking search (e.g., 'aws api key')")
    parser.add_argument("--limit", type=int, default=100, help="Limit results")
    parser.add_argument("--output", help="Output file (JSON)")
    parser.add_argument("--check-limit", action="store_true", help="Check rate limit")
    
    args = parser.parse_args()
    
    # Override token from args
    global GITHUB_TOKEN
    if args.token:
        GITHUB_TOKEN = args.token
        HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"
    
    # Check rate limit
    if args.check_limit:
        check_rate_limit()
        return
    
    if not GITHUB_TOKEN:
        print("[ERROR] No GitHub token. Set GITHUB_TOKEN env or use --token")
        print("[INFO] Example: export GITHUB_TOKEN='ghp_xxx'")
        return
    
    results = []
    
    # Organization analysis
    if args.org:
        print(f"\n[*] Analyzing organization: {args.org}")
        org_info = get_org_info(args.org)
        if org_info:
            print(f"[+] Name: {org_info.get('name', 'N/A')}")
            print(f"[+] Public repos: {org_info.get('public_repos', 0)}")
            print(f"[+] Followers: {org_info.get('followers', 0)}")
            results.append(org_info)
        
        repos = list_org_repos(args.org, args.limit)
        print(f"[+] Found {len(repos)} repos")
        for repo in repos[:10]:
            print(f"  - {repo['name']}: {repo.get('description', 'No description')}")
        results.extend(repos)
    
    # User analysis
    if args.user:
        print(f"\n[*] Analyzing user: {args.user}")
        user_info = get_user_info(args.user)
        if user_info:
            print(f"[+] Name: {user_info.get('name', 'N/A')}")
            print(f"[+] Public repos: {user_info.get('public_repos', 0)}")
            print(f"[+] Followers: {user_info.get('followers', 0)}")
            results.append(user_info)
        
        repos = list_user_repos(args.user, args.limit)
        print(f"[+] Found {len(repos)} repos")
        for repo in repos[:10]:
            print(f"  - {repo['name']}: {repo.get('description', 'No description')}")
        results.extend(repos)
    
    # Code search
    if args.search:
        items = search_code(args.search, args.limit)
        for item in items[:20]:
            print(f"  - {item.get('repository', {}).get('full_name')}: {item.get('name')}")
            print(f"    Path: {item.get('path')}")
        results.extend(items)
    
    # Repo search
    if args.repos:
        items = search_repos(args.repos, args.limit)
        for item in items[:20]:
            print(f"  - {item['full_name']}: {item.get('description', 'No description')}")
            print(f"    Stars: {item.get('stargazers_count', 0)} | Lang: {item.get('language', 'N/A')}")
        results.extend(items)
    
    # GitHub dorking
    if args.dorks:
        print(f"\n[*] GitHub Dorking: {args.dorks}")
        # Common dorking patterns
        dork_queries = [
            f"{args.dorks} language:python",
            f"{args.dorks} language:javascript", 
            f"{args.dorks} extension:env",
            f"{args.dorks} extension:config",
            f"{args.dorks} filename:.git-credentials"
        ]
        
        for query in dork_queries:
            items = search_code(query, 10)
            if items:
                print(f"\n[+] Results for: {query}")
                for item in items[:5]:
                    repo = item.get('repository', {})
                    print(f"  - {repo.get('full_name')}/{item.get('name')}")
            results.extend(items)
    
    # Save output
    if args.output and results:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Results saved to: {args.output}")

if __name__ == "__main__":
    main()