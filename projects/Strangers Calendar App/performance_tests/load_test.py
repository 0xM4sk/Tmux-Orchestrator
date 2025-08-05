|
import locust
from locust import HttpUser, task

class LoadTestUser(HttpUser):
@task
def test_calendar_creation(self):
self.client.post("/api/calendars", json={"name": "test calendar"})

@task
def test_availability_windows(self):
self.client.post("/api/availability", json={"start": "2025-08-01T09:00Z", "end": "2025-08-01T10:00Z"})

if __name__ == "__main__":
locust.main()