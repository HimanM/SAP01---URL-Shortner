# SAP01 URL Shortener

This is the first project of learning system architecture. It securely implements core distributed system elements, orchestrating precise interactions between backend processing, stream ingestion, performant caching, and a responsive frontend interface.

## High Level Architecture
The software comprises seamlessly integrated microservices:
* Frontend Service: A modern, minimalistic React application powered by Vite, utilizing Tailwind CSS for structural styling. Delivered using an efficient multi stage Nginx Docker container.
* API Service (Python/Flask): A stateless component solely responsible for mapping and generating short codes. This service conducts database writes for creation events and database reads against replicas during redirections.
* Analytics Service (Python/Flask): A specialized backend dedicated strictly to retrieving aggregated event states, database performance metrics, and system log diagnostics.
* Log Ingestion Worker: A persistent Python daemon running continuously. It polls Kafka topics to capture asynchronous click events and system trace logs, securely persisting them to the analytics database.

## Architecture Flow

1. URL Shortening: The user submits a URL to the API. The API creates a unique identifier, stores it in the primary PostgreSQL database, and publishes a system log event to Kafka.
2. Link Resolution: Accessing a short link checks the Redis cache first. On a cache miss, it reads from the PostgreSQL replica to minimize read pressure on the primary. It then updates the cache.
3. Asynchronous Analytics: Upon redirection, the API emits a click event to a Kafka topic. The background worker independently consumes this stream and writes into the analytics database, ensuring the main request loop remains unblocked and highly performant.
4. Logging: Distinct application events (Database writes, Cache misses) are serialized and delivered to a system logs topic, serving as a comprehensive application audit trail accessible via the frontend.

## Component Reasoning

* Nginx Load Balancer: Serves as a unified routing endpoint, seamlessly proxying static traffic and API requests while mitigating connection limits.
* Redis Caching: Placed intentionally to accelerate short code redirection lookups. Serving repeated requests from RAM eliminates disk I/O bottlenecks and drastically lowers database latency.
* PostgreSQL (Primary and Replica): Enforces structural data integrity. Utilizing a primary database strictly for write operations and an isolated replica strictly for reads guarantees robust parallel performance and fault tolerance.
* Kafka and Zookeeper: Captures URL click streams and system diagnostic logs. Utilizing an event stream prevents the main API from getting clogged doing repetitive analytics and insertion computation.

## Local Deployment
The repository functions out of the box leveraging Docker Compose.
