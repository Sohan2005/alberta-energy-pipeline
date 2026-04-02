# Lambda Deployment Notes

## Day 7 - Initial Setup
- Created Lambda function: alberta-energy-fetcher
- Runtime: Python 3.11
- Region: ca-central-1

## IAM Fix
- Reviewed auto-generated execution role
- Role has AWSLambdaBasicExecutionRole only
- Correct - Lambda only needs CloudWatch Logs access

## Day 8 - Real Pipeline Deployed
- Packaged fetch.py, transform.py, db.py, lambda_function.py
- Dependencies compiled using Amazon Linux Docker image
- Windows-compiled pydantic_core was incompatible with Lambda runtime
- Fix: MSYS_NO_PATHCONV=1 with explicit Windows path for Docker volume mount

## Day 9 - Configuration Fix
- Default timeout was 3 seconds - too short for pipeline execution
- Pipeline init alone takes 3+ seconds (loading supabase, httpx, pydantic)
- Fix: increased timeout to 60 seconds
- Default memory was 128MB - pipeline was using 116MB (90% usage)
- Fix: increased memory to 256MB for safe headroom