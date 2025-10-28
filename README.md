# Retrieval-Augmented Generation (RAG) System

A modular Retrieval-Augmented Generation (RAG) system built with FastAPI, MongoDB, Qdrant, and LLM integration.
Fully containerized with Docker Compose for easy deployment, and enhanced with Prometheus, Node Exporter, and Grafana for comprehensive monitoring and observability. This setup supports hybrid retrieval-based question answering and text generation pipelines, ensuring real-time insights into performance, scalability, and error rates.
The system is designed for production-grade scalability, with asynchronous processing for high-throughput ingestion and querying. It reduces LLM hallucinations by grounding responses in retrieved vector data while providing full traceability through versioned embeddings and query logs.



# Features

**FastAPI Backend** – High-performance REST API for ingestion, search, and query generation.
 
**MongoDB** – Persistent document and metadata store.
 
**Qdrant** – Vector database for semantic search and similarity retrieval.
 
**LLM Integration** – Dual provider support for embeddings and generation.

**Docker Compose** – Fully containerized multi-service environment.

**Prometheus + Grafana** – Complete metrics, monitoring, and visualization stack.
 
**Node Exporter** – Collects host-level system metrics.

**Scalable Modular Architecture** – Easily extendable for new data sources or LLM providers.


## Architecture Overview
```bash
            ┌───────────────────────────┐
            │         Client UI         │
            └────────────┬──────────────┘
                         │ REST API
                 ┌───────▼────────┐
                 │   FastAPI App  │
                 │ (RAG Service)  │
                 └───────┬────────┘
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌──────▼──────┐ ┌───────▼─────────┐
│   MongoDB     │ │   Qdrant    │ │  LLM Providers   │
│(Docs, Metadata│ │(Embeddings) │ │                  │
└───────────────┘ └─────────────┘ └──────────────────┘

                 ┌────────────────────────┐
                 │ Monitoring Stack        │
                 │ Prometheus + Grafana    │
                 │ + Node Exporter         │
                 └────────────────────────┘
```
# Steps
1. Create Environment File
```bash
cp env.example .env
```
2. Build and Run the Stack
```bash
docker compose up --build
```

The following services will be launched:

| Service               | Port    | Description           |
| --------------------- | ------- | --------------------- |
| **FastAPI (RAG API)** | `8000`  | Main backend service  |
| **MongoDB**           | `27017` | Document store        |
| **Qdrant**            | `6333`  | Vector search engine  |
| **Prometheus**        | `9090`  | Metrics collection    |
| **Grafana**           | `3000`  | Metrics dashboard     |
| **Node Exporter**     | `9100`  | Host metrics exporter |

# Monitoring & Metrics

Prometheus

URL: http://localhost:9090

Scrapes metrics from FastAPI, Qdrant, and Node Exporter.

Grafana

URL: http://localhost:3000

Default login → admin / admin

Add Prometheus as data source (http://prometheus:9090).

Import dashboards:

FastAPI Metrics

Node Exporter Full

# Development Mode

 Run FastAPI locally (without Docker):
 ```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

# Technologies

| Category          | Stack                                      |
| ----------------- | ------------------------------------------ |
| Backend           | FastAPI (Python)                           |
| Databases         | MongoDB, Qdrant                            |
| Vector Embeddings | OpenAI, Cohere                             |
| Monitoring        | Prometheus, Node Exporter, Grafana         |
| Containerization  | Docker, Docker Compose                     |
| Metrics           | Prometheus client + FastAPI instrumentator |

# License
 see the LICENSE file for details.

# Contributing

Pull requests are welcome!

