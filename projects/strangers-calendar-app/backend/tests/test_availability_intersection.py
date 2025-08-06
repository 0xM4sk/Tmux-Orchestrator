|
# backend/tests/test_availability_intersection.py

import pytest
from backend.calendar.intersection import find_availability_intersection

def test_overlapping_intervals():
window1 = (9, 12)
window2 = (10, 14)
result = find_availability_intersection(window1, window2)
assert result == (10, 12)

def test_no_overlap():
window1 = (9, 12)
window2 = (13, 15)
result = find_availability_intersection(window1, window2)
assert result is None

def test_edge_case_same_interval():
window1 = (9, 12)
window2 = (9, 12)
result = find_availability_intersection(window1, window2)
assert result == (9, 12)

def test_edge_case_partial_overlap():
window1 = (9, 12)
window2 = (8, 10)
result = find_availability_intersection(window1, window2)
assert result == (10, 10)