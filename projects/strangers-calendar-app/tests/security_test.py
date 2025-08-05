|
import lighthouse

def test_security():
report = lighthouse.run('http://localhost:5000')
print(report)

if __name__ == '__main__':
test_security()