# Deployment Guide - Indie Matching Engine

## Overview

This guide covers deploying the Indie Matching Engine to production environments.

---

## Pre-Deployment Checklist

### Security

- [ ] Change `API_KEY` from default value
- [ ] Store secrets in environment variables or secret manager (never in code)
- [ ] Review and restrict CORS origins in `app/main.py`
- [ ] Enable HTTPS/TLS for all connections
- [ ] Set up firewall rules (internal network only)
- [ ] Review database connection security (SSL mode)

### Configuration

- [ ] Set `LOG_LEVEL=WARNING` or `ERROR` for production
- [ ] Configure `DATABASE_URL` with production credentials
- [ ] Set appropriate `CACHE_TTL_SECONDS` based on data freshness needs
- [ ] Configure `MIN_RECOMMENDATION_SCORE` based on business requirements
- [ ] Review and customize `config/scoring_rules.yaml`
- [ ] Set `API_RELOAD=false` for production

### Database

- [ ] Run database migrations: `alembic upgrade head`
- [ ] Create database indexes (handled by migrations)
- [ ] Set up database backups
- [ ] Configure connection pooling settings
- [ ] Test database connectivity from app server

### Monitoring

- [ ] Set up application logging (centralized)
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Set up health check monitoring
- [ ] Create alerts for API errors and slow queries
- [ ] Monitor cache hit rates

---

## Deployment Methods

### Method 1: Docker (Recommended)

#### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8003/health')"

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "4"]
```

#### 2. Build and Run

```bash
# Build image
docker build -t indie-matching-engine:latest .

# Run container
docker run -d \
  --name matching-engine \
  -p 8003:8003 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@db-host:5432/indie_crm_core" \
  -e API_KEY="your-secure-api-key" \
  -e LOG_LEVEL="WARNING" \
  --restart unless-stopped \
  indie-matching-engine:latest
```

#### 3. Docker Compose (Multi-Service Setup)

```yaml
version: '3.8'

services:
  matching-engine:
    build: ./indie-matching-engine
    container_name: indie-matching-engine
    ports:
      - "8003:8003"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:${DB_PASSWORD}@postgres:5432/indie_crm_core
      API_KEY: ${MATCHING_ENGINE_API_KEY}
      LOG_LEVEL: WARNING
      ENABLE_MATCH_CACHING: "true"
      CACHE_TTL_SECONDS: 3600
    depends_on:
      - postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: indie_crm_core
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Method 2: Systemd Service (Linux Server)

#### 1. Create Service File

Create `/etc/systemd/system/indie-matching-engine.service`:

```ini
[Unit]
Description=Indie Matching Engine
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/indie-matching-engine
Environment="PATH=/opt/indie-matching-engine/venv/bin"
EnvironmentFile=/opt/indie-matching-engine/.env
ExecStart=/opt/indie-matching-engine/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Deploy and Start

```bash
# Copy application files
sudo cp -r indie-matching-engine /opt/
cd /opt/indie-matching-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Set permissions
sudo chown -R www-data:www-data /opt/indie-matching-engine

# Enable and start service
sudo systemctl enable indie-matching-engine
sudo systemctl start indie-matching-engine

# Check status
sudo systemctl status indie-matching-engine
```

### Method 3: Kubernetes

#### 1. Create Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: indie-matching-engine
  namespace: indiestack
spec:
  replicas: 3
  selector:
    matchLabels:
      app: matching-engine
  template:
    metadata:
      labels:
        app: matching-engine
    spec:
      containers:
      - name: matching-engine
        image: your-registry/indie-matching-engine:latest
        ports:
        - containerPort: 8003
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: matching-engine-secrets
              key: database-url
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: matching-engine-secrets
              key: api-key
        - name: LOG_LEVEL
          value: "WARNING"
        livenessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### 2. Create Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: matching-engine-service
  namespace: indiestack
spec:
  selector:
    app: matching-engine
  ports:
    - protocol: TCP
      port: 8003
      targetPort: 8003
  type: ClusterIP
```

---

## Database Migrations

### Running Migrations

```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field"

# Create empty migration
alembic revision -m "Manual migration"
```

---

## Scheduled Batch Processing

### Using Cron

Add to crontab to run batch matching daily at 2 AM:

```bash
0 2 * * * cd /opt/indie-matching-engine && /opt/indie-matching-engine/venv/bin/python cli.py compute-matches >> /var/log/matching-engine-batch.log 2>&1
```

### Using Airflow (Recommended for Complex Workflows)

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'indiestack',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'matching_engine_batch',
    default_args=default_args,
    description='Daily batch matching computation',
    schedule_interval='0 2 * * *',  # 2 AM daily
    catchup=False,
)

compute_matches = BashOperator(
    task_id='compute_all_matches',
    bash_command='cd /opt/indie-matching-engine && python cli.py compute-matches',
    dag=dag,
)
```

---

## Monitoring and Logging

### Application Logs

```bash
# View logs (systemd)
sudo journalctl -u indie-matching-engine -f

# View logs (Docker)
docker logs -f indie-matching-engine

# View logs (Kubernetes)
kubectl logs -f deployment/indie-matching-engine -n indiestack
```

### Health Monitoring

Set up monitoring for:

1. **HTTP Health Endpoint**: `GET /health`
   - Should return 200 with `{"status": "healthy"}`
   - Alert if returns 5xx or times out

2. **Database Connectivity**
   - Monitor connection pool stats
   - Alert on connection failures

3. **API Performance**
   - Track response times for `/api/v1/recommendations/*`
   - Alert if p95 > 1000ms

4. **Cache Hit Rate**
   - Monitor ratio of cached vs. computed matches
   - Alert if hit rate drops below 70%

### Metrics to Track

- API request rate
- API error rate (5xx responses)
- Average match score (from batch runs)
- Number of recommendations returned
- Cache staleness (time since last update)
- Database query performance

---

## Backup and Recovery

### Database Backups

```bash
# Backup matching engine tables
pg_dump -U user -h localhost -t buyer_listing_matches -t matching_runs indie_crm_core > matching_engine_backup.sql

# Restore
psql -U user -h localhost indie_crm_core < matching_engine_backup.sql
```

### Configuration Backups

Ensure `config/scoring_rules.yaml` is version controlled and backed up.

---

## Scaling Considerations

### Horizontal Scaling

The matching engine is **stateless** (aside from database) and can be horizontally scaled:

```bash
# Docker: Run multiple containers behind a load balancer
docker run -d --name matching-engine-1 -p 8003:8003 indie-matching-engine:latest
docker run -d --name matching-engine-2 -p 8004:8003 indie-matching-engine:latest

# Kubernetes: Increase replicas
kubectl scale deployment indie-matching-engine --replicas=5 -n indiestack
```

### Database Scaling

For high-volume environments:

1. **Read Replicas**: Configure read-only replicas for CRM data reads
2. **Connection Pooling**: Tune `pool_size` and `max_overflow` in `app/database.py`
3. **Caching**: Enable Redis for distributed caching (future enhancement)

### Performance Tuning

```python
# In app/database.py, adjust pool settings:
engine = create_async_engine(
    settings.database_url,
    pool_size=20,        # Increase for more concurrent connections
    max_overflow=40,     # Allow burst capacity
    pool_pre_ping=True,  # Verify connections before use
)
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Symptom**: `ConnectionRefusedError` or timeout errors

**Solutions**:
- Verify `DATABASE_URL` is correct
- Check database server is running and accessible
- Verify firewall rules allow connection
- Check SSL requirements: add `?sslmode=require` to URL if needed

#### 2. API Key Authentication Failures

**Symptom**: 403 Forbidden responses

**Solutions**:
- Verify `API_KEY` matches in client and server
- Check `X-API-Key` header is being sent
- Review environment variable loading

#### 3. Poor Match Quality

**Symptom**: Low match scores or irrelevant recommendations

**Solutions**:
- Review and tune `config/scoring_rules.yaml` weights
- Verify CRM data quality (null values, incorrect categories)
- Check `MIN_RECOMMENDATION_SCORE` threshold
- Run `python cli.py info` to review configuration

#### 4. Slow API Responses

**Symptom**: High latency on recommendation endpoints

**Solutions**:
- Enable match caching: `ENABLE_MATCH_CACHING=true`
- Pre-compute matches via batch job
- Add database indexes (already handled by migrations)
- Scale horizontally (add more instances)

---

## Security Best Practices

1. **Never commit secrets**: Use `.env` files (gitignored) or secret managers
2. **Use strong API keys**: Generate with `openssl rand -hex 32`
3. **Restrict network access**: Deploy on internal network only
4. **Enable HTTPS**: Use reverse proxy (nginx, Traefik) with TLS
5. **Regular updates**: Keep dependencies updated for security patches
6. **Audit logs**: Log all API access with user/service identifiers
7. **Rate limiting**: Add rate limiting to prevent abuse (via reverse proxy)

---

## Rollback Procedure

If issues arise after deployment:

```bash
# 1. Rollback Docker container
docker stop indie-matching-engine
docker run -d --name matching-engine indie-matching-engine:previous-version

# 2. Rollback database migrations
alembic downgrade -1

# 3. Rollback systemd service
sudo systemctl stop indie-matching-engine
# Replace binary with previous version
sudo systemctl start indie-matching-engine

# 4. Rollback Kubernetes deployment
kubectl rollout undo deployment/indie-matching-engine -n indiestack
```

---

## Post-Deployment Verification

After deployment, verify:

```bash
# 1. Service is running
curl http://your-server:8003/health

# 2. API is accessible (with auth)
curl -H "X-API-Key: your-api-key" http://your-server:8003/api/v1/matches/health

# 3. Database connectivity
# Should return empty recommendations if no data, not errors
curl -H "X-API-Key: your-api-key" http://your-server:8003/api/v1/recommendations/buyer/1

# 4. Run test batch computation
python cli.py compute-matches --buyer-id 1

# 5. Check logs for errors
# (see Monitoring section above)
```

---

## Maintenance

### Weekly

- [ ] Review error logs
- [ ] Check API performance metrics
- [ ] Verify batch jobs completed successfully

### Monthly

- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Review and tune scoring weights based on feedback
- [ ] Analyze cache hit rates and adjust TTL if needed
- [ ] Database vacuum and analyze (PostgreSQL)

### Quarterly

- [ ] Security audit (dependency scanning, penetration testing)
- [ ] Performance review and optimization
- [ ] Capacity planning review

---

## Support and Escalation

For production issues:

1. **Check logs** first (see Monitoring section)
2. **Review health endpoints** for service status
3. **Verify configuration** with `python cli.py info`
4. **Contact DevOps team** for infrastructure issues
5. **Contact development team** for application bugs

---

**Last Updated**: 2024-01-15
