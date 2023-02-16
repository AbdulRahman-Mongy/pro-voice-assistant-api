# Pull base image
FROM python:3.10.4-slim-bullseye
# Set environment variables
ENV DATABASE_URL "postgres://postgres@db/postgres"

# Set work directory
WORKDIR /code
# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# Copy project
COPY . .