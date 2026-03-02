import os

class Config:
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "classroom-crypto-key")
    
    RANDOM_ORG_API_KEY = "7cfb102e-14b9-4722-a089-deb4a058c636"
    RANDOM_ORG_URL = "https://api.random.org/json-rpc/4/invoke"
    ENTROPY_BYTES_REQUESTED = 16 
    MAX_ENTRIES = 1000