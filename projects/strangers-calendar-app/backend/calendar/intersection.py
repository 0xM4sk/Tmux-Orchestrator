|
# backend/calendar/intersection.py

def find_availability_intersection(window1, window2):
start_max = max(window1[0], window2[0])
end_min = min(window1[1], window2[1])
if start_max < end_min:
return (start_max, end_min)
else:
return None