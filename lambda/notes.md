# Lambda Deployment Notes

## Day 7 - Initial Setup

- Created Lambda function: alberta-energy-fetcher
- Runtime: Python 3.11
- Region: ca-central-1

## IAM Fix
- Reviewed auto-generated execution role: alberta-energy-fetcher-role-xxxxxxxx
- Role has AWSLambdaBasicExecutionRole only
- This is correct - Lambda only needs CloudWatch Logs access
- Outbound HTTP calls to AESO API and Supabase don't require AWS permissions
- Root credentials removed from concern - Lambda uses its execution role, not user credentials
- aws configure credentials are for CLI use only, not passed to Lambda