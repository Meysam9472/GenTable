from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
# get_remote_address uses the user's IP to track limits. Use Redis as the storage backend for rate limits.
# storage_uri="redis://redis:6379/0(0 is the database number)" 
limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv("SLOWAPI_URI"), 
                  default_limits=["20/minute"])