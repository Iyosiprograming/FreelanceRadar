from slowapi import Limiter
from slowapi.util import get_remote_address

# Global client rate limiter to protect endpoints from DoS and brute-force flooding.
# Default limit: 60 requests per minute per client IP address.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    headers_enabled=True,
)
