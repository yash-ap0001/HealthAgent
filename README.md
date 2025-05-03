# HealthAgent

A comprehensive health management system that consists of a Spring Boot backend with PostgreSQL database integration and a Python-based Health Sub-Agent that analyzes health data and generates insights.

## System Components

### 1. Spring Boot Backend

- REST APIs for authentication, health data management, and insights
- JWT authentication for secure access
- PostgreSQL database for data storage
- Flyway for database migrations

### 2. Python Health Sub-Agent

- Connects to the Spring Boot backend via REST APIs
- Analyzes health data (steps, sleep, heart rate)
- Generates actionable insights based on patterns
- Modular architecture for easy extension to more data types

## Health Data Types Supported

- **Steps**: Daily step counts from fitness trackers/apps
- **Sleep**: Sleep duration and patterns
- **Heart Rate**: Heart rate measurements and zones

## Getting Started

### Prerequisites

- Java 17+
- Maven 3.6+
- PostgreSQL 12+
- Python 3.9+
- pip (Python package manager)

### Backend Setup

1. Configure the database connection in `application.properties`

2. Run the Spring Boot application:
   ```
   cd spring-backend
   ./mvnw spring-boot:run
   ```
