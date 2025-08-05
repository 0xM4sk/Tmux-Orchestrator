|
import time
from selenium import webdriver

def test_performance():
driver = webdriver.Chrome()
start_time = time.time()
driver.get('http://localhost:5000')
end_time = time.time()
driver.quit()
print(f'Page load time: {end_time - start_time} seconds')

if __name__ == '__main__':
test_performance()