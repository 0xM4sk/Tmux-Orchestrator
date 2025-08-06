|
import datetime

class EphemeralAccessToken:
def __init__(self, expiration_time):
self.expiration_time = expiration_time

def get_ephemeral_access_token():
# Generate a temporary access token with an expiration time (e.g., 1 hour)
current_time = datetime.datetime.now()
expiration_time = current_time + datetime.timedelta(hours=1)
return EphemeralAccessToken(expiration_time)