# Password Reset Guide

## Scope
This guide applies to CloudOps Desk users who cannot sign in because they forgot a password, received an expired reset link, or entered too many failed login attempts.

## Standard reset flow
1. Open the CloudOps Desk sign-in page and select **Forgot password**.
2. Enter the email address used for the workspace account.
3. Check the inbox and spam folder for a reset email from `no-reply@cloudopsdesk.example`.
4. Use the reset link within 30 minutes. Expired links must be requested again.
5. Set a password with at least 12 characters, one uppercase letter, one lowercase letter, one number, and one symbol.

## Account lock behavior
After 5 failed login attempts in 15 minutes, the account is temporarily locked for 20 minutes. Support cannot bypass the lock without verifying the account owner. If the user is an administrator, confirm whether SSO is enforced before changing passwords.

## Troubleshooting
If the reset email is not received within 5 minutes, ask the user to confirm the email address, check spam filtering, and allow emails from the CloudOps Desk domain. If the user reports a reset link that opens a blank page, they should clear browser cache, use an incognito window, or try a different browser.

## Escalation criteria
Escalate to human support if the account remains locked after 20 minutes, if the account owner cannot be verified, if there is suspected unauthorized access, or if the user requests changes to administrator ownership.
