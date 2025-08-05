|
import re

def validate_phone_number(phone_number):
pattern = r'^\+?1?\d{9,15}$'
if re.match(pattern, phone_number):
return True
else:
return False