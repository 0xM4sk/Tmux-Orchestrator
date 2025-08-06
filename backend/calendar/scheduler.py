|
from .utils import find_availability_intersection

def find_available_slots(schedules):
available_slots = []
for schedule in schedules:
for i in range(len(schedule) - 1):
intersection = find_availability_intersection(schedule[i], schedule[i + 1])
if intersection:
available_slots.append(intersection)
return available_slots