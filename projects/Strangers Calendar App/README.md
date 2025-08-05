|
# Strangers Calendar App

## Deployment

To deploy the application, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/strangers-calendar-app.git
cd strangers-calendar-app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (e.g., `.env` file):
```ini
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///site.db
```

5. Run the application:
```bash
flask run
```

## Monitoring

To monitor the application, use tools like `gunicorn`, `nginx`, and `supervisor`.