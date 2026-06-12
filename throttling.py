from slowapi import Limiter
from slowapi.util import get_remote_address

# get_remote_address uses the user's IP to track limits. Use Redis as the storage backend for rate limits.
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://redis:6379/0", 
                  default_limits=["20/minute"])