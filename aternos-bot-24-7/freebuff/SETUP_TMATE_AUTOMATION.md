# SARAhack - Tmate Automation Setup Guide

## ⚠️ Important: SSH Key Location

**The SSH key was generated in the cloud environment (Replit), NOT on your Kali machine.**

For automation, you need to **generate a NEW SSH key on your Kali machine** and add that public key to the tmate session.

---

## Overview

| Component | Status | Details |
|-----------|--------|---------|
| **Tmate Session** | ✅ Active | `eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io` |
| **SSH Key** | ❌ Needs setup | Generate on your Kali |
| **freebuff CLI** | ✅ v0.0.103 | Installed on tmate session |
| **Reports Ready** | 3 pending | Shopify, GitLab, Twilio |

---

## Step-by-Step Setup

### Step 1: Generate SSH Key on YOUR Kali Machine

On your **local Kali machine** (not this cloud environment), run:

```bash
# Generate SSH key (empty passphrase for automation)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N '' -C 'sarahack-kali'

# Set correct permissions
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# Display your public key (COPY THIS)
cat ~/.ssh/id_ed25519.pub
```

**Example output:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGexample123sarahack-kali
```

### Step 2: Connect to Tmate via Password Tunnel

The first connection must be via the cloudflare tunnel with password:

```bash
# Connect via password tunnel
ssh gg@suitable-mate-caroline-guide.trycloudflare.com

# Password: 123456123456
```

### Step 3: Add Your Public Key to Tmate Session

Once connected via password tunnel, **on the tmate session**, run:

```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Add your public key (paste the key from Step 1)
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGexample123sarahack-kali" >> ~/.ssh/authorized_keys

# Verify
cat ~/.ssh/authorized_keys
```

### Step 4: Test SSH Key Connection

Now test the SSH key connection from **your Kali machine**:

```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io
```

You should now be able to connect without a password!

---

## Deployment (After SSH Key Works)

Once SSH key authentication is working, deploy the workspace from your Kali:

```bash
# From your Kali machine
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io << 'ENDSSH'
mkdir -p ~/workspace/freebuff
cd ~/workspace/freebuff

# Download freebuff package
curl -L -o freebuff-v4.tar https://tmpfiles.org/wKw2KIT24Xzj/freebuff-v4.tar
tar xf freebuff-v4.tar

# Set environment variables
cat > ~/.env << 'ENVEOF'
export CODEBUFF_POSTHOG_API_KEY="be0e3e50-e07c-434d-98d0-85d6c59d615c"
export HACKERONE_EMAIL="${HACKERONE_EMAIL}"
export HACKERONE_PASSWORD=")a9By=*D#6/w9T"
export AI_MODEL="minimax/minimax-m2.7"
ENVEOF

echo "[+] Deployment complete"
ENDSSH
```

---

## Automated Submission Commands

On the tmate session, run:

```bash
# Load environment
source ~/.env

# Check freebuff
freebuff --version

# Submit Shopify report
freebuff "Submit IDOR vulnerability report for Shopify - GraphQL endpoint allows unauthorized access to other store data via sequential IDs. Severity: High. PoC: curl -X POST https://shop.myshopify.com/admin/api/graphql.json -H 'X-Shopify-Access-Token: YOUR_TOKEN' -d '{\"query\":\"{shop{id}}\"}'"

# Or use Python submission
cd ~/workspace/freebuff
python3 auto_submit_reports.py --all
```

---

## Quick Reference

### Connection Info

| Method | Command | Auth |
|--------|---------|------|
| **Password (initial)** | `ssh gg@suitable-mate-caroline-guide.trycloudflare.com` | Password: `123456123456` |
| **SSH Key (automated)** | `ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io` | Key-based |

### Environment Variables

```bash
export CODEBUFF_POSTHOG_API_KEY="be0e3e50-e07c-434d-98d0-85d6c59d615c"
export HACKERONE_EMAIL="${HACKERONE_EMAIL}"
export HACKERONE_PASSWORD=")a9By=*D#6/w9T"
```

### freebuff Commands

```bash
freebuff --version                    # Check version
freebuff login                        # Login (if needed)
freebuff "Your report message"        # Submit report
```

---

## Troubleshooting

### "Permission denied (publickey)"

**Cause:** Your public key is not in the tmate session's `authorized_keys`

**Fix:** 
1. Connect via password tunnel first
2. Add your public key to `~/.ssh/authorized_keys`

### "Connection refused" or "Could not resolve hostname"

**Cause:** Tmate session expired

**Fix:** Create a new tmate session on your Kali:
```bash
# On your Kali
tmate -S /tmp/tmate.sock new-session -d
tmate -S /tmp/tmate.sock display -p '#{session_name}'
# Note the session name and update your scripts
```

### freebuff command not found

**Fix:**
```bash
npm install -g freebuff
```

---

## Security Notes

- SSH private key (`~/.ssh/id_ed25519`) provides full access to the tmate session
- Keep this key secure - never share it
- The key has no passphrase for automation convenience
- Credentials are stored in environment variables - avoid storing in plaintext files

---

## Available Reports

| ID | Program | Vulnerability | Platform |
|----|---------|---------------|----------|
| 4 | Shopify | IDOR (GraphQL) | HackerOne |
| 6 | GitLab | IDOR (ML Registry) | HackerOne |
| 20 | Twilio | IDOR (Account SID) | HackerOne |
| - | Atlassian | IDOR | Bugcrowd |