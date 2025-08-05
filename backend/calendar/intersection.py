|
# Availability Intersection Algorithm
from datetime import datetime, timedelta

def find_intersection(window1, window2):
start1, end1 = window1
start2, end2 = window2

latest_start = max(start1, start2)
earliest_end = min(end1, end2)

if latest_start < earliest_end:
return (latest_start, earliest_end)
else:
return None

def test_find_intersection():
assert find_intersection((datetime(2023, 9, 1, 10), datetime(2023, 9, 1, 12)), 
(datetime(2023, 9, 1, 11), datetime(2023, 9, 1, 13))) == (datetime(2023, 9, 1, 11), datetime(2023, 9, 1, 12))
assert find_intersection((datetime(2023, 9, 1, 10), datetime(2023, 9, 1, 12)), 
(datetime(2023, 9, 1, 14), datetime(2023, 9, 1, 16))) is None
assert find_intersection((datetime(2023, 9, 1, 10), datetime(2023, 9, 1, 12)), 
(datetime(2023, 9, 1, 10), datetime(2023, 9, 1, 10))) is None
assert find_intersection((datetime(2023, 9, 1, 10), datetime(2023, 9, 1, 12)), 
(datetime(2023, 9, 1, 12), datetime(2023, 9, 1, 14))) is None