# GitHub Actions Secret Fix Required

## Issue
The `VITE_API_URL` GitHub Actions secret is currently set to:
```
https://app.laurayoga.co.uk
```

## Required Fix
Update the GitHub Actions secret to include the full API path:
```
https://app.laurayoga.co.uk/api/v1
```

##Steps to Fix
1. Go to GitHub repository settings
2. Navigate to Secrets and variables → Actions
3. Edit the `VITE_API_URL` secret
4. Change value from `https://app.laurayoga.co.uk` to `https://app.laurayoga.co.uk/api/v1`
5. Save the secret

## Why This is Needed
The frontend build process uses `VITE_API_URL` at build time to configure the API base URL. Without `/api/v1`, API calls go to:
- Wrong: `https://app.laurayoga.co.uk/auth/register` (404)
- Correct: `https://app.laurayoga.co.uk/api/v1/auth/register` (works)

## Current Workaround
Manually building frontend locally with:
```bash
VITE_API_URL=https://app.laurayoga.co.uk/api/v1 VITE_USE_MOCK_API=false npm run build
```

Then deploying via SCP.

## Verification
After fixing the secret and running a deployment, verify the JavaScript contains the correct URL:
```bash
ssh root@server "grep -o 'baseUrl.*api/v1' /opt/yogaflow/frontend/dist/assets/index-*.js"
```

Should return: `baseUrl:"https://app.laurayoga.co.uk/api/v1"`
