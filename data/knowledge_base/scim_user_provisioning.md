# SCIM User Provisioning Guide

## Overview
SCIM provisioning is available for Enterprise workspaces. It automates user creation, deactivation, and group assignment from supported identity providers.

## Required configuration
Generate a SCIM bearer token from Workspace Settings > Identity > SCIM. Configure the identity provider with the SCIM base URL and bearer token. The token is shown only once and must be stored securely.

## Supported operations
CloudOps Desk supports Create User, Update User, Deactivate User, List Users, and Group Push. Hard deletion is not supported through SCIM.

## Common errors
A 401 response means the SCIM bearer token is missing or invalid. A 409 response means a user with the same email already exists. A 422 response means a required field is missing or invalid.

## Escalation criteria
Escalate if deactivated users retain access, if group mappings produce incorrect roles, or if the customer suspects provisioning created unauthorized access.
