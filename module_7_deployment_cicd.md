# 🚀 Module 7 — Deployment & CI/CD

This tutorial covers deploying your Azure GenAI RAG system using containerization, Azure App Service, Azure Kubernetes Service (AKS), and Azure DevOps CI/CD pipelines.

---

## 📚 Table of Contents

1. [Introduction to Containerization](#introduction-to-containerization)
2. [Docker Basics](#docker-basics)
3. [Containerizing Your FastAPI Application](#containerizing-your-fastapi-application)
4. [Azure App Service Deployment](#azure-app-service-deployment)
5. [Azure Kubernetes Service (AKS)](#azure-kubernetes-service-aks)
6. [Azure DevOps CI/CD](#azure-devops-cicd)
7. [Monitoring & Autoscaling](#monitoring--autoscaling)
8. [Hands-On: Complete CI/CD Pipeline](#hands-on-complete-cicd-pipeline)

---

## 🐳 Introduction to Containerization

### What is Containerization?

Containerization packages an application and its dependencies into a lightweight, portable container that runs consistently across different environments.

**Benefits**:
- **Consistency**: Same environment in dev, test, and production
- **Isolation**: Applications don't interfere with each other
- **Portability**: Run anywhere Docker is supported
- **Scalability**: Easy to scale horizontally
- **Resource Efficiency**: Lower overhead than VMs

### Docker vs Virtual Machines

| Feature | Containers | Virtual Machines |
|---------|-----------|------------------|
| Isolation | Process-level | OS-level |
| Startup Time | Seconds | Minutes |
| Resource Usage | Low | High |
| Portability | High | Medium |
| Overhead | Minimal | Significant |

---

## 🐋 Docker Basics

### Key Concepts

1. **Dockerfile**: Blueprint for building images
2. **Image**: Read-only template for creating containers
3. **Container**: Running instance of an image
4. **Registry**: Repository for storing images (Docker Hub, Azure Container Registry)

### Essential Docker Commands

```bash
# Build an image
docker build -t myapp:latest .

# Run a container
docker run -p 8000:8000 myapp:latest

# List running containers
docker ps

# List all containers
docker ps -a

# Stop a container
docker stop <container_id>

# Remove a container
docker rm <container_id>

# List images
docker images

# Remove an image
docker rmi <image_id>

# View logs
docker logs <container_id>

# Execute command in running container
docker exec -it <container_id> /bin/bash
```

---

## 📦 Containerizing Your FastAPI Application

### Step 1: Create Dockerfile

**File**: `Dockerfile`

```dockerfile
# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create .dockerignore

**File**: `.dockerignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual environments
venv/
env/
ENV/
azure-genai/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment files
.env
.env.local

# Git
.git/
.gitignore

# Documentation
*.md
docs/

# Docker
Dockerfile
.dockerignore

# CI/CD
.github/
.azure/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

### Step 3: Add Health Check Endpoint

**File**: `api/main.py` (update)

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.routers.chat import router as chat_router
from api.routers.embed import router as embed_router
from api.routers.ask import router as ask_router
from api.routers.graphask import router as graphask_router

app = FastAPI(title="GenAI API", version="1.0.0")

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(embed_router, prefix="/embed", tags=["Embedding"])
app.include_router(ask_router, prefix="/ask", tags=["Ask"])
app.include_router(graphask_router, prefix="/graphask", tags=["GraphRAG"])

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "GenAI API"}
    )

@app.get("/")
async def root():
    return {"message": "Azure GenAI API", "version": "1.0.0"}
```

### Step 4: Build and Test Locally

```bash
# Build the image
docker build -t azure-genai-api:latest .

# Run the container
docker run -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT="your-endpoint" \
  -e AZURE_OPENAI_API_KEY="your-key" \
  -e AZURE_OPENAI_DEPLOYMENT_NAME="gpt4o" \
  azure-genai-api:latest

# Test the health endpoint
curl http://localhost:8000/health

# Test an API endpoint
curl http://localhost:8000/docs
```

### Step 5: Multi-Stage Dockerfile (Optimized)

For production, use a multi-stage build to reduce image size:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ☁️ Azure App Service Deployment

### Overview

Azure App Service is a Platform-as-a-Service (PaaS) that simplifies deploying web applications without managing infrastructure.

**Features**:
- Automatic scaling
- Built-in load balancing
- SSL/TLS certificates
- Deployment slots (Blue/Green)
- Integrated monitoring

### Step 1: Create Azure Container Registry (ACR)

```bash
# Login to Azure
az login

# Create resource group (if not exists)
az group create --name azure-genai --location canadaeast

# Create Azure Container Registry
az acr create \
  --resource-group azure-genai \
  --name yourregistryname \
  --sku Basic \
  --admin-enabled true

# Login to ACR
az acr login --name yourregistryname

# Get ACR login server
az acr show --name yourregistryname --query loginServer --output tsv
```

### Step 2: Build and Push Image to ACR

```bash
# Build image
docker build -t azure-genai-api:latest .

# Tag image for ACR
docker tag azure-genai-api:latest yourregistryname.azurecr.io/azure-genai-api:latest

# Push to ACR
docker push yourregistryname.azurecr.io/azure-genai-api:latest

# List images in ACR
az acr repository list --name yourregistryname --output table
```

### Step 3: Create App Service Plan

```bash
# Create App Service Plan (Linux, container)
az appservice plan create \
  --name azure-genai-plan \
  --resource-group azure-genai \
  --location canadaeast \
  --is-linux \
  --sku B1
```

### Step 4: Create Web App

```bash
# Create Web App
az webapp create \
  --resource-group azure-genai \
  --plan azure-genai-plan \
  --name your-app-name \
  --deployment-container-image-name yourregistryname.azurecr.io/azure-genai-api:latest

# Configure ACR credentials
az webapp config container set \
  --name your-app-name \
  --resource-group azure-genai \
  --docker-custom-image-name yourregistryname.azurecr.io/azure-genai-api:latest \
  --docker-registry-server-url https://yourregistryname.azurecr.io \
  --docker-registry-server-user $(az acr credential show --name yourregistryname --query username -o tsv) \
  --docker-registry-server-password $(az acr credential show --name yourregistryname --query passwords[0].value -o tsv)
```

### Step 5: Configure Environment Variables

```bash
# Set environment variables
az webapp config appsettings set \
  --resource-group azure-genai \
  --name your-app-name \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-key" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt4o" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="embedding-small" \
    AZURE_OPENAI_API_VERSION="2024-08-01-preview" \
    AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net" \
    AZURE_SEARCH_API_KEY="your-key" \
    AZURE_SEARCH_INDEX_NAME="docs-index"
```

### Step 6: Enable Continuous Deployment

```bash
# Enable continuous deployment from ACR
az webapp deployment container config \
  --name your-app-name \
  --resource-group azure-genai \
  --enable-cd true
```

### Step 7: Configure Scaling

```bash
# Configure autoscaling
az monitor autoscale create \
  --resource-group azure-genai \
  --resource /subscriptions/{subscription-id}/resourceGroups/azure-genai/providers/Microsoft.Web/serverfarms/azure-genai-plan \
  --name azure-genai-autoscale \
  --min-count 1 \
  --max-count 10 \
  --count 2

# Add autoscale rule (CPU-based)
az monitor autoscale rule create \
  --resource-group azure-genai \
  --autoscale-name azure-genai-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

# Add autoscale rule (scale in)
az monitor autoscale rule create \
  --resource-group azure-genai \
  --autoscale-name azure-genai-autoscale \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1
```

### Step 8: Deployment Slots (Blue/Green)

```bash
# Create staging slot
az webapp deployment slot create \
  --resource-group azure-genai \
  --name your-app-name \
  --slot staging

# Deploy to staging
az webapp deployment slot swap \
  --resource-group azure-genai \
  --name your-app-name \
  --slot staging \
  --target-slot production
```

---

## ☸️ Azure Kubernetes Service (AKS)

### Overview

AKS provides managed Kubernetes for container orchestration with advanced features like auto-scaling, rolling updates, and service mesh.

### Step 1: Create AKS Cluster

```bash
# Create AKS cluster
az aks create \
  --resource-group azure-genai \
  --name azure-genai-aks \
  --node-count 2 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --node-vm-size Standard_B2s

# Get credentials
az aks get-credentials \
  --resource-group azure-genai \
  --name azure-genai-aks
```

### Step 2: Create Kubernetes Manifests

**File**: `k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: azure-genai-api
  labels:
    app: azure-genai-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: azure-genai-api
  template:
    metadata:
      labels:
        app: azure-genai-api
    spec:
      containers:
      - name: azure-genai-api
        image: yourregistryname.azurecr.io/azure-genai-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-genai-secrets
              key: azure-openai-endpoint
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-genai-secrets
              key: azure-openai-api-key
        - name: AZURE_OPENAI_DEPLOYMENT_NAME
          value: "gpt4o"
        - name: AZURE_OPENAI_EMBEDDING_DEPLOYMENT
          value: "embedding-small"
        - name: AZURE_SEARCH_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-genai-secrets
              key: azure-search-endpoint
        - name: AZURE_SEARCH_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-genai-secrets
              key: azure-search-api-key
        - name: AZURE_SEARCH_INDEX_NAME
          value: "docs-index"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: azure-genai-api-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: azure-genai-api
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: azure-genai-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: azure-genai-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**File**: `k8s/secrets.yaml` (template - don't commit actual secrets)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: azure-genai-secrets
type: Opaque
stringData:
  azure-openai-endpoint: "https://your-resource.openai.azure.com/"
  azure-openai-api-key: "your-key"
  azure-search-endpoint: "https://your-search.search.windows.net"
  azure-search-api-key: "your-key"
```

### Step 3: Deploy to AKS

```bash
# Create namespace
kubectl create namespace azure-genai

# Create secrets (use kubectl create secret or Azure Key Vault)
kubectl create secret generic azure-genai-secrets \
  --from-literal=azure-openai-endpoint="https://your-resource.openai.azure.com/" \
  --from-literal=azure-openai-api-key="your-key" \
  --from-literal=azure-search-endpoint="https://your-search.search.windows.net" \
  --from-literal=azure-search-api-key="your-key" \
  --namespace azure-genai

# Apply deployment
kubectl apply -f k8s/deployment.yaml -n azure-genai

# Check deployment status
kubectl get pods -n azure-genai
kubectl get services -n azure-genai

# Get external IP
kubectl get service azure-genai-api-service -n azure-genai
```

### Step 4: Configure Ingress (Optional)

**File**: `k8s/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: azure-genai-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: azure-genai-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: azure-genai-api-service
            port:
              number: 80
```

---

## 🔄 Azure DevOps CI/CD

### Overview

Azure DevOps provides end-to-end DevOps toolchain including:
- **Azure Repos**: Git repositories
- **Azure Pipelines**: CI/CD automation
- **Azure Artifacts**: Package management
- **Azure Boards**: Work tracking

### Step 1: Create Azure DevOps Project

1. Go to [dev.azure.com](https://dev.azure.com)
2. Create a new organization (if needed)
3. Create a new project: "azure-genai-rag"

### Step 2: Push Code to Azure Repos

```bash
# Initialize git (if not already)
git init

# Add Azure DevOps remote
git remote add origin https://dev.azure.com/your-org/azure-genai-rag/_git/azure-genai-rag

# Add files
git add .

# Commit
git commit -m "Initial commit: Azure GenAI RAG system"

# Push to Azure Repos
git push -u origin main
```

### Step 3: Create Build Pipeline (CI)

**File**: `azure-pipelines.yml`

```yaml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    exclude:
    - README.md
    - '*.md'

pool:
  vmImage: 'ubuntu-latest'

variables:
  dockerRegistryServiceConnection: 'azure-genai-acr'
  imageRepository: 'azure-genai-api'
  containerRegistry: 'yourregistryname.azurecr.io'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile'
  tag: '$(Build.BuildId)'
  vmImageName: 'ubuntu-latest'

stages:
- stage: Build
  displayName: 'Build and Push Docker Image'
  jobs:
  - job: Build
    displayName: 'Build Docker Image'
    steps:
    - task: Docker@2
      displayName: 'Build and push image to ACR'
      inputs:
        command: buildAndPush
        repository: $(imageRepository)
        dockerfile: $(dockerfilePath)
        containerRegistry: $(dockerRegistryServiceConnection)
        tags: |
          $(tag)
          latest

    - task: PublishTestResults@2
      displayName: 'Publish Test Results'
      condition: always()
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/test-results.xml'
        failTaskOnFailedTests: true

- stage: Test
  displayName: 'Run Tests'
  dependsOn: Build
  jobs:
  - job: Test
    displayName: 'Run Unit Tests'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.11'
        displayName: 'Use Python 3.11'

    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
      displayName: 'Install dependencies'

    - script: |
        pytest tests/ --junitxml=junit/test-results.xml --cov=api --cov-report=xml
      displayName: 'Run tests'
      continueOnError: true

    - task: PublishCodeCoverageResults@1
      displayName: 'Publish Code Coverage'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: '$(System.DefaultWorkingDirectory)/**/coverage.xml'

- stage: SecurityScan
  displayName: 'Security Scanning'
  dependsOn: Build
  jobs:
  - job: SecurityScan
    displayName: 'Scan Docker Image'
    steps:
    - task: Docker@2
      displayName: 'Scan image for vulnerabilities'
      inputs:
        command: login
        containerRegistry: $(dockerRegistryServiceConnection)

    - script: |
        docker pull $(containerRegistry)/$(imageRepository):$(tag)
        # Add security scanning tool (e.g., Trivy, Snyk)
        # trivy image $(containerRegistry)/$(imageRepository):$(tag)
      displayName: 'Run security scan'
```

### Step 4: Create Release Pipeline (CD)

**File**: `azure-pipelines-release.yml`

```yaml
trigger: none

pool:
  vmImage: 'ubuntu-latest'

variables:
  dockerRegistryServiceConnection: 'azure-genai-acr'
  imageRepository: 'azure-genai-api'
  containerRegistry: 'yourregistryname.azurecr.io'
  resourceGroup: 'azure-genai'
  appServiceName: 'your-app-name'
  aksClusterName: 'azure-genai-aks'
  aksNamespace: 'azure-genai'

stages:
- stage: DeployToStaging
  displayName: 'Deploy to Staging'
  jobs:
  - deployment: DeployStaging
    displayName: 'Deploy to App Service Staging'
    environment: 'staging'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebAppContainer@1
            displayName: 'Deploy to App Service Staging Slot'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              appName: $(appServiceName)
              deployToSlotOrASE: true
              resourceGroupName: $(resourceGroup)
              slotName: 'staging'
              containers: '$(containerRegistry)/$(imageRepository):$(Build.BuildId)'

          - task: AzureCLI@2
            displayName: 'Run Smoke Tests'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                STAGING_URL=$(az webapp show --name $(appServiceName) --resource-group $(resourceGroup) --slot staging --query defaultHostName -o tsv)
                curl -f https://$STAGING_URL/health || exit 1

- stage: DeployToProduction
  displayName: 'Deploy to Production'
  dependsOn: DeployToStaging
  condition: succeeded()
  jobs:
  - deployment: DeployProduction
    displayName: 'Deploy to Production'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebAppContainer@1
            displayName: 'Deploy to App Service Production'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              appName: $(appServiceName)
              deployToSlotOrASE: false
              resourceGroupName: $(resourceGroup)
              containers: '$(containerRegistry)/$(imageRepository):$(Build.BuildId)'

          - task: AzureCLI@2
            displayName: 'Deploy to AKS'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az aks get-credentials --resource-group $(resourceGroup) --name $(aksClusterName)
                kubectl set image deployment/azure-genai-api azure-genai-api=$(containerRegistry)/$(imageRepository):$(Build.BuildId) -n $(aksNamespace)
                kubectl rollout status deployment/azure-genai-api -n $(aksNamespace)

          - task: AzureCLI@2
            displayName: 'Run Production Smoke Tests'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                PROD_URL=$(az webapp show --name $(appServiceName) --resource-group $(resourceGroup) --query defaultHostName -o tsv)
                curl -f https://$PROD_URL/health || exit 1
```

### Step 5: Blue/Green Deployment Strategy

**File**: `azure-pipelines-blue-green.yml`

```yaml
trigger: none

pool:
  vmImage: 'ubuntu-latest'

variables:
  dockerRegistryServiceConnection: 'azure-genai-acr'
  imageRepository: 'azure-genai-api'
  containerRegistry: 'yourregistryname.azurecr.io'
  resourceGroup: 'azure-genai'
  appServiceName: 'your-app-name'

stages:
- stage: BlueGreenDeploy
  displayName: 'Blue/Green Deployment'
  jobs:
  - deployment: BlueGreen
    displayName: 'Blue/Green Deployment'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          # Deploy to staging (green)
          - task: AzureWebAppContainer@1
            displayName: 'Deploy to Staging (Green)'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              appName: $(appServiceName)
              deployToSlotOrASE: true
              resourceGroupName: $(resourceGroup)
              slotName: 'staging'
              containers: '$(containerRegistry)/$(imageRepository):$(Build.BuildId)'

          # Health check on green
          - task: AzureCLI@2
            displayName: 'Health Check Green'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                GREEN_URL=$(az webapp show --name $(appServiceName) --resource-group $(resourceGroup) --slot staging --query defaultHostName -o tsv)
                for i in {1..10}; do
                  if curl -f https://$GREEN_URL/health; then
                    echo "Health check passed"
                    exit 0
                  fi
                  sleep 5
                done
                echo "Health check failed"
                exit 1

          # Swap slots (green becomes production)
          - task: AzureCLI@2
            displayName: 'Swap to Production'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az webapp deployment slot swap \
                  --resource-group $(resourceGroup) \
                  --name $(appServiceName) \
                  --slot staging \
                  --target-slot production

          # Verify production
          - task: AzureCLI@2
            displayName: 'Verify Production'
            inputs:
              azureSubscription: 'azure-genai-subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                PROD_URL=$(az webapp show --name $(appServiceName) --resource-group $(resourceGroup) --query defaultHostName -o tsv)
                curl -f https://$PROD_URL/health || exit 1
```

---

## 📊 Monitoring & Autoscaling

### Application Insights Integration

**File**: `api/main.py` (add monitoring)

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
import logging
import os

# Configure Application Insights
config_integration.trace_integrations(['requests', 'logging'])

logger = logging.getLogger(__name__)
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    logger.addHandler(AzureLogHandler(
        connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    ))

app = FastAPI(title="GenAI API", version="1.0.0")

# Add middleware for request tracking
@app.middleware("http")
async def log_requests(request: Request, call_next):
    tracer = Tracer(
        exporter=AzureExporter(
            connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
        ),
        sampler=ProbabilitySampler(1.0)
    )
    
    with tracer.span(name=request.url.path):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "custom_dimensions": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            }
        )
        
        return response

# ... rest of your routes
```

### Create Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app azure-genai-insights \
  --location canadaeast \
  --resource-group azure-genai

# Get connection string
az monitor app-insights component show \
  --app azure-genai-insights \
  --resource-group azure-genai \
  --query connectionString -o tsv
```

### Configure Alerts

```bash
# Create alert for high response time
az monitor metrics alert create \
  --name "High Response Time" \
  --resource-group azure-genai \
  --scopes /subscriptions/{subscription-id}/resourceGroups/azure-genai/providers/Microsoft.Insights/components/azure-genai-insights \
  --condition "avg requests/duration > 2000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email your-email@example.com
```

### Dashboard Configuration

Create a dashboard in Azure Portal or use Azure Monitor Workbooks to visualize:
- Request rates
- Response times
- Error rates
- CPU/Memory usage
- Custom metrics

---

## 🎯 Hands-On: Complete CI/CD Pipeline

### Step 1: Set Up Repository Structure

```
azure-genai/
├── api/
│   ├── main.py
│   └── ...
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── azure-pipelines.yml
├── k8s/
│   ├── deployment.yaml
│   └── ingress.yaml
└── tests/
    └── test_api.py
```

### Step 2: Create Service Connections in Azure DevOps

1. Go to Project Settings → Service connections
2. Create Docker Registry connection to ACR
3. Create Azure Resource Manager connection

### Step 3: Set Up Pipeline

1. Go to Pipelines → New Pipeline
2. Select Azure Repos Git
3. Choose your repository
4. Select "Existing Azure Pipelines YAML file"
5. Choose `azure-pipelines.yml`

### Step 4: Configure Environments

1. Go to Pipelines → Environments
2. Create "staging" environment
3. Create "production" environment with approval gates

### Step 5: Test the Pipeline

```bash
# Make a change and push
git add .
git commit -m "Update API"
git push origin main

# Pipeline will automatically trigger
# Monitor in Azure DevOps → Pipelines
```

### Step 6: Monitor Deployment

1. Check pipeline runs in Azure DevOps
2. Monitor Application Insights
3. Test endpoints:
   ```bash
   curl https://your-app-name.azurewebsites.net/health
   curl https://your-app-name.azurewebsites.net/docs
   ```

---

## ✅ Best Practices

### Security

1. **Secrets Management**: Use Azure Key Vault
2. **Image Scanning**: Scan for vulnerabilities
3. **Least Privilege**: Use managed identities
4. **Network Security**: Use private endpoints
5. **HTTPS Only**: Enforce SSL/TLS

### Performance

1. **Caching**: Use Redis Cache for frequent queries
2. **CDN**: Use Azure CDN for static content
3. **Connection Pooling**: Reuse database connections
4. **Async Operations**: Use async/await in FastAPI

### Reliability

1. **Health Checks**: Implement comprehensive health checks
2. **Retry Logic**: Add retry with exponential backoff
3. **Circuit Breakers**: Prevent cascade failures
4. **Graceful Shutdown**: Handle shutdown signals

### Cost Optimization

1. **Right-Sizing**: Choose appropriate VM sizes
2. **Reserved Instances**: Use for predictable workloads
3. **Auto-Scaling**: Scale down during low usage
4. **Monitoring**: Track and optimize costs

---

## 🎓 Summary

In this module, you learned:

- ✅ Containerization with Docker
- ✅ Deploying to Azure App Service
- ✅ Kubernetes deployment with AKS
- ✅ Azure DevOps CI/CD pipelines
- ✅ Blue/Green deployment strategies
- ✅ Monitoring and autoscaling
- ✅ Best practices for production deployments

**Next Steps**:
- Set up your CI/CD pipeline
- Deploy your RAG system to production
- Configure monitoring and alerts
- Implement blue/green deployments
- Optimize for cost and performance

---

## 📚 Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/azure/aks/)
- [Azure DevOps Pipelines](https://docs.microsoft.com/azure/devops/pipelines/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

