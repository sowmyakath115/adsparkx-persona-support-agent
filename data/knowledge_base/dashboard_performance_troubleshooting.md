# Dashboard Performance Troubleshooting

## Symptoms
Customers may report slow dashboards, delayed widgets, timeout errors, or stale metrics. Performance issues can be caused by large date ranges, high-cardinality filters, browser extensions, network latency, or incident-related backend delays.

## Recommended checks
- Reduce the dashboard date range to the last 24 hours.
- Remove high-cardinality filters such as user_id or request_id.
- Refresh in an incognito browser window.
- Check whether other users in the workspace experience the same slowdown.
- Export the underlying data if a report is needed immediately.

## Expected behavior
Most dashboards load within 5 seconds for 30-day views. Large workspaces and complex filters may require up to 30 seconds.

## Escalation criteria
Escalate if dashboards fail for multiple users, if critical operational reporting is blocked, or if dashboard data appears incorrect after refresh.
