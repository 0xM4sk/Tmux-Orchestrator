|
import re

def validate_phone_number(phone_number):
"""Validate phone number format."""
pattern = r'^\+?\d{10,15}$'
if re.match(pattern, phone_number):
return True
else:
return False