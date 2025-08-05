|
# phone_number_validation.py

import re

def validate_phone_number(phone_number):
"""
Validate a phone number using regex.

Args:
phone_number (str): The phone number to validate.

Returns:
bool: True if the phone number is valid, False otherwise.
"""
pattern = r'^\+?1?\d{9,15}$'
return re.match(pattern, phone_number) is not None