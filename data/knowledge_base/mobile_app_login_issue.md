# Mobile App Login Issues

## Supported platforms
The CloudOps Desk mobile app supports iOS 16 or later and Android 10 or later. Users on older operating systems should use the web app until they can update their device.

## Troubleshooting steps
1. Confirm the app is updated to the latest version from the app store.
2. Switch from mobile data to Wi-Fi or from Wi-Fi to mobile data.
3. Clear the app cache on Android or reinstall the app on iOS.
4. Confirm the user can sign in from the web app.
5. If SSO is enabled, test whether the identity provider login page opens in the system browser.

## Known behavior
After a password reset, mobile sessions may take up to 5 minutes to refresh. Users can force refresh by closing and reopening the app.

## Escalation criteria
Escalate if the web app works but mobile login fails across multiple devices, or if the app crashes before the login screen.
