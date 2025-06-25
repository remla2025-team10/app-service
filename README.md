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
  
### Example Metrics

The application exports the following types of metrics:

#### Counter Example
Counters are cumulative metrics that only increase over time:

```text
python_gc_objects_collected_total{generation="0"} 161.0
Metric: python_gc_objects_collected_total
Labels: generation
```

```text
user_feedback_total{feedback="yes",sentiment="example prediction result",version="1.10.5"} 1.0
Metric: user_feedback_total
Labels: feedback, sentiment, version
```

#### Gauge Example
Gauges represent values that can go up and down:

```text
process_virtual_memory_bytes 8.79845376e+08
Metric: process_virtual_memory_bytes
Labels: none
```

```text
app_info{version="1.10.5"} 1.0
Metric: app_info
Labels: version
```

#### Histogram Example
Histograms track the distribution of values:

```text
flask_http_request_duration_seconds_bucket{endpoint="metrics.record_feedback",le="0.005",method="POST",status="200"} 1.0
Metric: flask_http_request_duration_seconds_bucket
Labels: endpoint, le (bucket boundary), method, status
```

Histograms also include sum and count metrics:
```text
flask_http_request_duration_seconds_count{endpoint="metrics.record_feedback",method="POST",status="200"} 1.0
Metric: flask_http_request_duration_seconds_count
Labels: endpoint, method, status

flask_http_request_duration_seconds_sum{endpoint="metrics.record_feedback",method="POST",status="200"} 0.001169801000287407
Metric: flask_http_request_duration_seconds_sum
Labels: endpoint, method, status
```

#### Summary Example
Summaries provide percentile calculations:

```text
sentiment_analysis_duration_seconds{version="2",quantile="0.5"} 0.042
Metric: sentiment_analysis_duration_seconds
Labels: version, quantile (percentile)
```

Like histograms, summaries include sum and count metrics:
```text
sentiment_analysis_duration_seconds_sum{version="2"} 53.2
Metric: sentiment_analysis_duration_seconds_sum
Labels: version

sentiment_analysis_duration_seconds_count{version="2"} 312
Metric: sentiment_analysis_duration_seconds_count
Labels: version
```

You can integrate these metrics into a Prometheus server and visualize them using Grafana.

For A/B testing, specific metrics are available at `http://localhost:5000/api/metrics/prometheus` to compare performance between versions.

---

## A/B Testing Implementation

This application implements A/B testing to evaluate new features and their impact on user engagement. The testing is conducted between two versions of the application:

### Test Versions

- **Version A (v1)**: The stable version from the `main` branch, which provides the base sentiment analysis functionality with standard feedback options.

- **Version B (v2)**: The experimental version from the `enhanced-app` branch, which extends the base functionality with additional UI elements (such as encouraging GIF animations) designed to increase user engagement and feedback submission rates.

### Testing Configuration

When deployed with the `operation` repository setup, the application uses Istio's traffic management features to split traffic between versions:

- Users with the header `x-user: experiment` are directed to Version B (v2)
- By default, 90% of traffic goes to Version A (v1) and 10% to Version B (v2)

### Metrics Collection

The application collects the following A/B testing metrics via the Prometheus integration:

- **Conversion rates**: The percentage of users who submit feedback after receiving sentiment analysis
- **Feedback distribution**: Comparison of positive vs. negative feedback between versions
- **Performance metrics**: Response times and processing durations to ensure Version B doesn't negatively impact performance

These metrics are available at the `/api/metrics` endpoint and can be visualized in Grafana dashboards to make data-driven decisions about which version performs better.

### Viewing Test Results

To analyze the A/B test results:
1. Deploy both versions using the `operation` repository
2. Access the Prometheus metrics at `http://prometheus.local`
3. View the pre-configured Grafana dashboard at `http://grafana.local` to compare version performance

For more detailed information about the continuous experimentation approach, refer to the documentation in the `operation` repository.

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

