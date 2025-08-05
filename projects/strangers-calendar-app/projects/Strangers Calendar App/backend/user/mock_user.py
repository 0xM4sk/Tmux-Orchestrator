|
# Mock user implementation
def register_user(username, password):
print(f"Registering user {username}")
return f"User-{username}"

def login_user(username, password):
print(f"Logging in user {username}")
if username == "admin" and password == "admin":
return True
return False