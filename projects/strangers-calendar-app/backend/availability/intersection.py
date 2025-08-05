|
def intersect_availability(user1_availability, user2_availability):
# Find common availability
start = max(user1_availability['start'], user2_availability['start'])
end = min(user1_availability['end'], user2_availability['end'])
return {'start': start, 'end': end}