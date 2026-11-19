# CloudDesk API and support policy, version 1

## API-01: Current API limits
This is the current policy. Team allows 60 API requests per minute per workspace. Business allows 300 requests per minute per workspace. Limits are shared by all API keys in that workspace. Free has no API access. HTTP 429 means the request exceeded the limit. Respect the Retry-After header before retrying, and use exponential backoff if that header is absent. Repeated immediate retries are not recommended.
An archived 2024 article stated that Team allowed 100 requests per minute. That article is superseded by this current 60-request limit.

## SUPPORT-01: Support coverage
Email support operates Monday-Friday, 09:00-17:00 UTC, excluding public holidays. Team has a next-business-day first-response target. Business has a 4-business-hour first-response target. These are first-response targets, not resolution guarantees. No plan includes a guaranteed weekend response under this policy. The assistant cannot create tickets, inspect live service status, or promise resolution times. For an active incident, the customer can contact support@clouddesk.example and include a workspace ID and the observed error.
