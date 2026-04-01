# Lambda Deployment Notes

## Day 7 - Initial Setup

- Created Lambda function: alberta-energy-fetcher
- Runtime: Python 3.11
- Region: ca-central-1

## IAM Note (to fix)
- Currently using root account AWS credentials in aws configure
- Need to create a dedicated IAM execution role with least privilege
- Root credentials should never be used for application workloads