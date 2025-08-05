|
# Strangers Calendar App

## Overview

The Strangers Calendar App is a social calendar application that allows users to share events with friends and family.

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip

### Installation

```sh
git clone https://github.com/your-repo/strangers-calendar.git
cd strangers-calendar
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Running the App

```sh
flask run
```

## Testing

```sh
pytest
```

## OAuth Authentication

For OAuth authentication, follow these steps:

- Register your application with Google and Apple.
- Configure the `auth_config.py` file with your client IDs and secrets.

## Deployment

The application is deployed to a production environment using Heroku. See the [deployment instructions](DEPLOYMENT.md).

## Maintenance

Regular maintenance tasks are performed by running the `maintenance.sh` script:

```sh
./scripts/maintenance.sh
```

These tasks can also be automated using GitHub Actions.

## Documentation

For more detailed documentation, see the [API documentation](docs/API.md) and the [User Guide](docs/USER_GUIDE.md).