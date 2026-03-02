import os

class Config:
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = True # Doesnt matter for local use
    SECRET_KEY = os.environ.get("SECRET_KEY", "classroom-crypto-key") # You can change this to be more secure, but its not really needed
    
    RANDOM_ORG_API_KEY = "REPLACE-THIS-WITH-YOUR-API-KEY" # Here you place your api key that you can get on https://api.random.org/
    RANDOM_ORG_URL = "https://api.random.org/json-rpc/4/invoke"
    ENTROPY_BYTES_REQUESTED = 16 # You can change this lower to save bytes on random.org, but you are losing quality of randomness.
    MAX_ENTRIES = 1000 # Limit of how much people or things can be in the selection at once.
