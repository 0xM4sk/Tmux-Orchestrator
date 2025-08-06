|
import pytest
from backend.calendar.scheduler import find_available_slots, find_availability_intersection

def test_find_available_slots():
schedules = [
[(9, 12), (14, 16)],
[(8, 10), (11, 13)],
[(15, 17), (18, 20)]
]
expected = [(10, 12), (14, 15), (17, 18)]
result = find_available_slots(schedules)
assert sorted(result) == sorted(expected)

def test_find_available_slots_no_overlap():
schedules = [
[(9, 12)],
[(13, 16)],
[(17, 20)]
]
expected = []
result = find_available_slots(schedules)
assert result == expected

def test_find_availability_intersection():
interval1 = (9, 12)
interval2 = (11, 14)
expected = (11, 12)
result = find_availability_intersection(interval1, interval2)
assert result == expected

def test_find_availability_intersection_no_overlap():
interval1 = (9, 10)
interval2 = (11, 12)
expected = None
result = find_availability_intersection(interval1, interval2)
assert result is None

def test_find_availability_intersection_edge_case_same_interval():
interval1 = (9, 12)
interval2 = (9, 12)
expected = (9, 12)
result = find_availability_intersection(interval1, interval2)
assert result == expected

def test_find_availability_intersection_edge_case_partial_overlap():
interval1 = (9, 12)
interval2 = (8, 10)
expected = (10, 10)
result = find_availability_intersection(interval1, interval2)
assert result == expected