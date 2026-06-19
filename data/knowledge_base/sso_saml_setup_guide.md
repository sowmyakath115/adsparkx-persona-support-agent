# SSO SAML Setup Guide

## Overview
CloudOps Desk supports SAML 2.0 single sign-on for Business and Enterprise workspaces. Administrators can configure identity providers such as Okta, Azure AD, Google Workspace, and OneLogin.

## Required SAML fields
- Entity ID: `https://auth.cloudopsdesk.example/saml/metadata`
- Assertion Consumer Service URL: `https://auth.cloudopsdesk.example/saml/acs`
- Name ID format: Email address
- Required attribute: `email`
- Optional attributes: `first_name`, `last_name`, `department`, `role`

## Setup steps
1. Create a SAML application in the identity provider.
2. Copy the CloudOps Desk Entity ID and ACS URL into the provider.
3. Upload the identity provider metadata XML into CloudOps Desk.
4. Map the email attribute to the user's primary email address.
5. Test SSO with a non-owner administrator before enforcing SSO for all users.

## Common errors
`invalid_audience` means the Entity ID does not match. `missing_email_attribute` means the assertion does not include a usable email field. `user_not_assigned` means the user has not been assigned to the SAML app in the identity provider.

## Escalation criteria
Escalate if the workspace owner is locked out after SSO enforcement, if metadata upload fails, or if a customer requests emergency SSO disablement.
