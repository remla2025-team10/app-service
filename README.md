# app-service

## Description

This is the app repository for the remla25-team10 project (backend and frontend). The app performs sentiment analysis for a short restaurant review that is provided by the user. `app-service` is responsible for invoking machine learning model service and returning the results to the user. It is a [Flask](https://flask.palletsprojects.com/en/stable/) application that exposes a REST API for the frontend to interact with.

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

The application will start on `http://localhost:5000` by default. You can change the host and port by modifying the `.env` file.

### Image

The image is on https://github.com/remla2025-team10/app-service/pkgs/container/app-service. You can use it with:

```bash
docker pull ghcr.io/remla2025-team10/app-service:latest
```

## Development

### Versioning

This repository uses **Semantic Versioning** and increase version number by commit message. The app gets its own version number by reading `VERSION` file, which is automatically generated during _release packing_ phase. 

The file is not in the repository but in the release pack.

