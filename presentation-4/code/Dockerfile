# Dockerfile
# This Dockerfile demonstrates:
# - Multi-stage builds for lean images
# - Distroless base for improved security
# - A health check to ensure responsiveness
# - Setting environment variables to control resource usage

##############################
# Build stage
##############################
FROM python:3.10-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user -r requirements.txt

##############################
# Runtime stage
##############################
FROM gcr.io/distroless/python3
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY ./src /app/src
COPY ./models /app/models

ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:$PATH
ENV MALLOC_ARENA_MAX=2
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD ["python","src/health_check.py"]

EXPOSE 8080
CMD ["python", "src/main.py"]
