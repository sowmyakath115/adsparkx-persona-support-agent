# Webhook Delivery Troubleshooting

## Delivery behavior
CloudOps Desk sends webhook events with a 10-second timeout. Delivery is considered successful when the customer endpoint returns a 2xx status code. Redirect responses are not followed.

## Retry policy
If delivery fails, CloudOps Desk retries after 1 minute, 5 minutes, 30 minutes, 2 hours, and 12 hours. Events are retained for 72 hours. After 72 hours, undelivered events expire and cannot be replayed automatically.

## Common causes
- Endpoint returns 401, 403, 404, 429, or 5xx.
- TLS certificate is expired or the certificate chain is incomplete.
- Customer firewall blocks CloudOps Desk outbound IP ranges.
- Signature verification fails because the webhook secret was rotated.
- Endpoint takes longer than 10 seconds to respond.

## Troubleshooting steps
Check the webhook delivery log, request ID, response status, response body, and latency. Verify the endpoint accepts POST requests and responds quickly before starting heavy processing. Recreate the webhook secret only after confirming the receiver configuration.

## Escalation criteria
Escalate if delivery logs show successful 2xx responses but the customer system did not process the event, if events are missing from the delivery log, or if the issue affects production integrations.
