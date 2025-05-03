# app-service

## Description

This is the app service for the remla25-team10 project. The app performs sentiment analysis for a short restaurant review that is provided by the user. `app-service` is responsible for invoking machine learning model service and returning the results to the user. It is a [Flask](https://flask.palletsprojects.com/en/stable/) application that exposes a REST API for the frontend to interact with.

This project includes automated release and versioning using GitHub Actions. The release process is triggered by a push to the main branch, and the version is automatically incremented based on the type of changes made (major, minor, or patch). The versioning follows [Semantic Versioning](https://semver.org/).

## Getting Started

### Prerequisites

- `Python 3.10` or higher
- `pip`

Install the required packages using pip:

```bash
pip install -r requirements.txt
```
### Running the Application

To run the application, use the following command:

```bash
python run.py
```

The application will start on `http://localhost:5000` by default. You can change the host and port by modifying the `run.py` file.

## Development

### Release Versioning

Use the following commands to create a new release when committing to the branch:

```bash
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z
```