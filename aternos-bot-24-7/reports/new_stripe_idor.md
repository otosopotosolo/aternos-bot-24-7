# 🚨 SUBMISSION PACKAGE: Stripe IDOR (BOLA)
# Platform: HackerOne
# Program: Stripe
# Date: 2026-06-06
# Status: TESTING REQUIRED - NOT YET CONFIRMED

---

## ⚠️ IMPORTANT: Research Required Before Submission

Based on current research, Stripe's core API has very strong IDOR protection. 
This template is for testing Stripe Connect or third-party integrations.

**Do NOT submit until vulnerability is confirmed!**

---

## TITLE:
```
IDOR in Stripe Connect API Allows Platform Partner to Access Other Merchant Data
```

---

## SEVERITY: High (if confirmed)

---

## SUMMARY:
```
An Insecure Direct Object Reference (IDOR) / BOLA vulnerability was discovered in Stripe Connect platform API that may allow a platform partner or connected account to access data belonging to other merchants on the platform by manipulating account IDs or API key scopes.

The vulnerability would exist if the platform fails to properly verify that the API key or OAuth token has appropriate permissions to access the requested account's data.
```

---

## VULNERABILITY DETAILS:

### Testing Scope:
- **HackerOne:** https://hackerone.com/stripe
- **In-Scope:** Check official scope page before testing!
- **Test Mode:** Always use test mode API keys (`sk_test_...`)

### Authentication:
- **Secret Key:** `sk_test_...` (test mode)
- **Publishable Key:** `pk_test_...` (test mode)

### Testing Methodology:

#### Step 1: Create Stripe Account (if not already)
```bash
# Go to https://dashboard.stripe.com/test/apikeys
# Copy your test API keys (sk_test_...)
```

#### Step 2: Create Two Test Accounts (for BOLA testing)

**Account A (Victim):**
- Create a Stripe account
- Note the `acct_` account ID
- Create some test data (customers, payments)

**Account B (Attacker):**
- Create another Stripe account  
- Note the `acct_` account ID

#### Step 3: Test Cross-Account Access

```bash
# As Account B, try to access Account A's data

# Test 1: List Account A's customers
curl https://api.stripe.com/v1/customers?account=acct_VICTIM_ID \\
  -u sk_test_ATTACKER_KEY:

# Test 2: Access Account A's balance
curl https://api.stripe.com/v1/balance?account=acct_VICTIM_ID \\
  -u sk_test_ATTACKER_KEY:

# Test 3: List Account A's payments
curl https://api.stripe.com/v1/payment_intents?account=acct_VICTIM_ID \\
  -u sk_test_ATTACKER_KEY:

# If data returned = IDOR CONFIRMED!
```

#### Step 4: Test Connect Platform Access

```bash
# Using platform API key, try to access connected account data

# List all connected accounts
curl https://api.stripe.com/v1/accounts \\
  -u sk_test_PLATFORM_KEY:

# Try accessing specific account
curl https://api.stripe.com/v1/accounts/acct_VICTIM_ID \\
  -u sk_test_PLATFORM_KEY:

# Try listing customers of specific account
curl https://api.stripe.com/v1/customers?account=acct_VICTIM_ID \\
  -u sk_test_PLATFORM_KEY:
```

---

## POC (To be completed after testing):

```bash
# STEP 1: Authenticate
# Obtain sk_test_API_KEY from Stripe Dashboard

# STEP 2: Create test data on Account A (Victim)
# Create customers, payments, subscriptions

# STEP 3: Attempt access from Account B (Attacker)
# Use Account B's API key to try accessing Account A's data

# STEP 4: Document findings
# If data returned = IDOR CONFIRMED
# Document exactly what data was accessible
```

---

## IMPACT (To be updated after testing):
- **Confidentiality:** High - Access to other merchants' financial data
- **Integrity:** Medium - Potential for unauthorized transactions
- **Availability:** None

### CVSS 3.1 Score: 7.5 (estimated, requires verification)

---

## REMEDIATION (To be updated after testing):
1. Implement strict authorization checks on all API endpoints
2. Verify account ownership before returning data
3. Use proper OAuth scope validation
4. Add audit logging for cross-account access attempts

---

## TESTING CHECKLIST:

- [ ] Create Stripe test account
- [ ] Enable test mode API keys
- [ ] Create two separate accounts (A and B)
- [ ] Test cross-account data access
- [ ] Document any successful unauthorized access
- [ ] Verify vulnerability is in-scope before reporting
- [ ] Update this template with actual POC

---

## REFERENCES:
- Stripe Security: https://docs.stripe.com/security
- Stripe Testing: https://docs.stripe.com/testing
- Stripe Connect: https://docs.stripe.com/connect
- OWASP BOLA: https://owasp.org/www-project-api-security/

---

## NOTES:
⚠️ **CRITICAL:** Stripe's core API is very secure. IDOR vulnerabilities are 
extremely rare. Focus testing on:
1. Stripe Connect platform features
2. Third-party integrations using Stripe
3. Webhook implementations

Always verify scope before testing and use only test mode!