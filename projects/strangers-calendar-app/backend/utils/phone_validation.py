|
import re

def is_valid_phone_number(phone_number):
pattern = r'^\+?1?\d{9,15}$'
return re.match(pattern, phone_number) is not None