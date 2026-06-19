# API Authentication Troubleshooting

## Common symptoms
API authentication failures usually appear as HTTP 401 or HTTP 403 responses. A 401 response means the token is missing, expired, malformed, or signed with an invalid secret. A 403 response means the token is valid but does not have the required role, workspace, or feature scope.

## Required checks
- Confirm the `Authorization: Bearer <token>` header is present.
- Verify the token was issued for the same workspace as the API endpoint.
- Check that the token has not expired. Access tokens expire after 60 minutes.
- Confirm the system clock is synchronized. Clock drift greater than 3 minutes can invalidate token signatures.
- For service accounts, confirm the account has the `api.read`, `api.write`, or `admin.audit` scope required by the endpoint.

## Root cause guidance
Most authentication incidents are caused by expired tokens, workspace mismatch, missing scopes, or secrets rotated without updating the application configuration. If the issue started after a deployment, compare environment variables for `CLOUDOPS_CLIENT_ID`, `CLOUDOPS_CLIENT_SECRET`, and `CLOUDOPS_WORKSPACE_ID`.

## Logs to capture
Capture timestamp, workspace ID, endpoint path, status code, request ID, and the OAuth client ID. Do not send raw access tokens or client secrets in support tickets.

## Escalation criteria
Escalate if valid scoped credentials still fail, if there is evidence of token leakage, or if the customer needs a security review.
