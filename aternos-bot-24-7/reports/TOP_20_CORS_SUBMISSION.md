# TOP 20 CORS Vulnerabilities - พร้อม Submit

## แนะนำให้ Submit เฉพาะตัวนี้ก่อน (20 reports)

---

## 1. Rollbar (CRITICAL) - https://hackerone.com/rollbar/reports/new

**API:** https://api.rollbar.com/api/1

**CORS Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Impact:** Arbitrary origin + credentials = ขโมย session ได้จากเว็บไซต์ malicious

**PoC:**
```bash
curl -I -X OPTIONS 'https://api.rollbar.com/api/1' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 2. Mailgun (CRITICAL) - security@mailgun.net

**API:** https://api.mailgun.net/v3/users

**CORS Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง email campaigns และ subscriber data

**PoC:**
```bash
curl -I -X OPTIONS 'https://api.mailgun.net/v3/users' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 3. CDN77 (CRITICAL) - Via their bug bounty program

**API:** https://api.cdn77.com/v2

**CORS Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง CDN statistics และ billing data

**PoC:**
```bash
curl -I -X OPTIONS 'https://api.cdn77.com/v2' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 4. Travis CI (CRITICAL) - https://hackerone.com/travis-ci/reports/new

**API:** https://api.travis-ci.org/builds

**CORS Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง build logs และ repository access tokens

**PoC:**
```bash
curl -I -X OPTIONS 'https://api.travis-ci.org/builds' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 5. Spotify (CRITICAL) - https://hackerone.com/spotify/reports/new

**API:** https://api.spotify.com/v1

**CORS Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง user playlists, listening history, และ premium data

**PoC:**
```bash
curl -I -X OPTIONS 'https://api.spotify.com/v1/me' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 6. Twilio Verify (CRITICAL) - https://hackerone.com/twilio/reports/new

**API:** https://verify.twilio.com/v1

**CORS Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง 2FA verification codes และ phone verification

**PoC:**
```bash
curl -I -X OPTIONS 'https://verify.twilio.com/v1' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 7. VictorOps (CRITICAL) - https://hackerone.com/victorops/reports/new

**API:** https://api.victorops.com/api/v1

**CORS Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง incident management และ on-call schedules

**PoC:**
```bash
curl -I -X OPTIONS 'https://api.victorops.com/api/v1' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 8. Discord (HIGH) - https://hackerone.com/discord/reports/new

**API:** https://discord.com/api/v10/users/@me

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** สูงมาก! Discord ใช้ cookie-based auth → ขโมย session ได้

**PoC:**
```bash
curl -I -X OPTIONS 'https://discord.com/api/v10/users/@me' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 9. Stripe (HIGH) - https://hackerone.com/stripe/reports/new หรือ Email security@stripe.com

**API:** https://api.stripe.com/v1/customers

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง billing data และ payment methods

**PoC:**
```bash
curl -I -X OPTIONS 'https://api.stripe.com/v1/customers' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 10. Twilio (HIGH) - https://hackerone.com/twilio/reports/new

**API:** https://api.twilio.com/2010-04-01

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง call logs, SMS history, และ phone numbers

**PoC:**
```bash
curl -I -X OPTIONS 'https://api.twilio.com/2010-04-01' -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET'
```

---

## 11. Pipedrive (HIGH) - https://hackerone.com/pipedrive/reports/new

**API:** https://api.pipedrive.com/v1

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง CRM data, deals, และ customer info

---

## 12. SendGrid (HIGH) - security@sendgrid.com หรือ https://hackerone.com/sendgrid/reports/new

**API:** https://api.sendgrid.com/v3

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง email marketing data และ contact lists

---

## 13. WordPress.com (HIGH) - https://hackerone.com/automattic/reports/new

**API:** https://public-api.wordpress.com/wp/v2

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง blog posts, user data, และ site analytics

---

## 14. New Relic (HIGH) - https://hackerone.com/newrelic/reports/new

**API:** https://api.newrelic.com/v2

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง application monitoring data และ infrastructure metrics

---

## 15. Atlassian (HIGH) - https://hackerone.com/atlassian/reports/new

**API:** https://api.atlassian.com/me

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง Jira, Confluence data และ user info

---

## 16. ClickUp (HIGH) - https://hackerone.com/clickup/reports/new

**API:** https://api.clickup.com/api/v2

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง tasks, projects, และ team data

---

## 17. GitLab (MEDIUM) - https://hackerone.com/gitlab/reports/new

**API:** https://gitlab.com/api/v4

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Methods: GET,POST,PUT,PATCH,DELETE
```

**Impact:** เข้าถึง source code และ repository data

---

## 18. Slack (MEDIUM) - https://hackerone.com/slack/reports/new

**API:** https://slack.com/api/conversations.list

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** สูง! Slack ใช้ cookie-based auth → session hijacking

---

## 19. Figma (MEDIUM) - https://hackerone.com/figma/reports/new

**API:** https://api.figma.com/v1

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง design files และ team projects

---

## 20. Bitbucket (MEDIUM) - https://hackerone.com/bitbucket/reports/new

**API:** https://api.bitbucket.org/2.0

**CORS Headers:**
```
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**Impact:** เข้าถึง source code repositories และ user data

---

## วิธี Submit

### สำหรับ HackerOne programs:
1. ไปที่ https://hackerone.com/[program]/reports/new
2. Copy report template จาก `reports/new_[program]_cors_[timestamp].md`
3. Paste และ submit

### สำหรับ Email submission:
- **Stripe:** security@stripe.com
- **SendGrid:** security@sendgrid.com
- **Mailgun:** security@mailgun.com

---

## Report Files ที่มีอยู่แล้ว

```bash
ls reports/new_*_cors_*.md | head -50
```

---

*Generated by SARAhack Mass CORS Scanner on 2026-06-07*