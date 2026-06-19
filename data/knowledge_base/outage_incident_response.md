# Outage and Incident Response

## Incident severity
Severity 1 means a production outage prevents most customers from using a critical workflow. Severity 2 means a major feature is degraded for a subset of customers. Severity 3 means a partial degradation or workaround exists.

## Customer communication
For active incidents, provide concise status, customer impact, known workaround, and next update timing if available in the status page or incident notes. Do not guess root cause or promise an exact restoration time unless the incident commander has published it.

## Workarounds
If dashboards are delayed, customers can use API exports for recent records. If webhook delivery is delayed, customers should keep receiver endpoints online because retries will continue according to the webhook retry policy.

## Internal escalation
Escalate immediately if a customer reports production downtime, data loss, multiple users affected, or executive escalation. Include customer workspace ID, affected feature, start time, business impact, and screenshots or request IDs.
