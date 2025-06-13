# app-service

## Description

This is the app repository for the remla25-team10 project (backend and frontend). The app performs sentiment analysis for a short restaurant review that is provided by the user. `app-service` is responsible for invoking machine learning model service and returning the results to the user. It is a [Flask](https://flask.palletsprojects.com/en/stable/) application that exposes a REST API for the frontend to interact with.

This project includes automated release and versioning using GitHub Actions. The release process is triggered by a push to the main branch, and the version is automatically incremented based on the type of changes made (major, minor, or patch). The versioning follows [Semantic Versioning](https://semver.org/).

---

## Getting Started

### Prerequisites

- `Python 3.10` or higher
- `pip`

Install the required packages using pip:

```bash
pip install -r requirements.txt
```

---

## Running the Application

### Running Locally

To run the application locally, use the following command:

```bash
python run.py
```

The application will start on `http://localhost:5000` by default. You can change the host and port by modifying the `.env` file.

### Running with Docker

To run the application using Docker, use the following commands:

1. Build the Docker image:
   ```bash
   docker build -t app-service .
   ```

2. Run the Docker container:
   ```bash
   docker run -p 5000:5000 app-service
   ```

Alternatively, you can pull the pre-built image from GitHub Container Registry:

```bash
docker pull ghcr.io/remla2025-team10/app-service:latest
docker run -p 5000:5000 ghcr.io/remla2025-team10/app-service:latest
```

---

## Prometheus Metrics

This application supports Prometheus metrics for monitoring and observability. The following endpoints are available:

- **Prometheus Metrics**:  
  Exposes all metrics in Prometheus format.  
  URL: `http://localhost:5000/api/metrics/prometheus`

- **A/B Testing Metrics**:  
  Provides metrics specifically for A/B testing, such as feedback counts, prediction clicks, and conversion rates.  
  URL: `http://localhost:5000/api/metrics/prometheus/ab_metrics`

### Example Metrics

- `feedback_count`: Count of feedback responses (labeled by version, feedback type, and sentiment).
- `prediction_clicks`: Number of prediction button clicks (labeled by version).
- `feedback_conversion_rate`: Conversion rate percentage (feedback/clicks, labeled by version).

You can integrate these metrics into a Prometheus server and visualize them using Grafana.

For A/B testing, you can visit `http://localhost:5000/api/metrics/prometheus/ab_metrics` to get the Prometheus-formatted metrics for the A/B testing branches.

```text
# HELP feedback_count Count of feedback responses
# TYPE feedback_count gauge
feedback_count{feedback="yes",sentiment="example prediction result",version="2"} 5.0
feedback_count{feedback="no",sentiment="example prediction result",version="2"} 1.0
# HELP prediction_clicks Number of prediction button clicks by version
# TYPE prediction_clicks gauge
prediction_clicks{version="1"} 0.0
prediction_clicks{version="2"} 10.0
# HELP feedback_conversion_rate Conversion rate percentage (feedback/clicks)
# TYPE feedback_conversion_rate gauge
feedback_conversion_rate{version="1"} 0.0
feedback_conversion_rate{version="2"} 60.0
```

---

## A/B Testing Branches

This repository uses two branches for A/B testing:

- **`main` branch**:  
  Represents the stable version of the application. Automatically released as `v1` and `latest`.

- **`enhanced_app` branch**:  
  Represents the experimental version of the application. Automatically released as `v2`.

The setup in `operation` repository allows you to run A/B tests by routing traffic to different versions (`v1` and `v2`) and collecting metrics to evaluate their performance.

---

## Development

### Versioning

This repository uses **Semantic Versioning** and increases the version number based on commit messages. The app gets its own version number by reading the `VERSION` file, which is automatically generated during the _release packing_ phase. 

The `VERSION` file is not included in the repository but is part of the release package.

---

## Future Improvements

- Add more detailed metrics for user behavior analysis.
- Implement traffic splitting logic for A/B testing directly in the application.
- Provide Helm charts for Kubernetes deployment.

