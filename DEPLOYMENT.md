# Deployment guide

This document explains how to ship the FastAPI service using container images. It covers a local Docker Compose run (for parity w
ith production) and a reference deployment to Azure Container Apps. Adapt the Azure steps if you prefer App Service, AKS, or an
other orchestrator — the image and environment variables remain the same.

---

## 1. Build + run with Docker Compose

1. Ensure Docker Desktop or the Docker Engine is installed.
2. Clone this repository and navigate to the root folder.
3. Build the image and start the stack:

   ```bash
   docker compose up --build -d
   ```

   * The API will be available on `http://localhost:8000`.
   * Meeting data is stored inside the named `data` volume declared in `compose.yaml`.
4. Tail logs as needed:

   ```bash
   docker compose logs -f
   ```

5. Tear down the containers (while preserving the volume) when you are finished:

   ```bash
   docker compose down
   ```

---

## 2. Publish the container image to Azure Container Registry (ACR)

1. Authenticate with Azure and select your subscription:

   ```bash
   az login
   az account set --subscription <subscription-id>
   ```

2. Create a resource group and ACR (skip if they already exist):

   ```bash
   az group create --name sahith-ai-rg --location eastus
   az acr create --resource-group sahith-ai-rg --name sahithaiacr --sku Basic
   ```

3. Build and push the image to ACR:

   ```bash
   az acr build --registry sahithaiacr --image sahith-ai-bot:latest .
   ```

   The command uses ACR Tasks so you do not need Docker running locally; it uploads the repo context, builds in Azure, and stores
the resulting image inside `sahithaiacr.azurecr.io`.

---

## 3. Deploy to Azure Container Apps

1. Enable the Microsoft.App namespace for your subscription:

   ```bash
   az provider register --namespace Microsoft.App
   az provider register --namespace Microsoft.OperationalInsights
   ```

2. Create a Container Apps environment and log analytics workspace:

   ```bash
   az monitor log-analytics workspace create \
       --resource-group sahith-ai-rg \
       --workspace-name sahith-ai-logs \
       --location eastus

   az containerapp env create \
       --name sahith-ai-env \
       --resource-group sahith-ai-rg \
       --logs-workspace-id $(az monitor log-analytics workspace show --resource-group sahith-ai-rg --workspace-name sahith-ai-log
s --query customerId -o tsv) \
       --logs-workspace-key $(az monitor log-analytics workspace get-shared-keys --resource-group sahith-ai-rg --workspace-name 
sahith-ai-logs --query primarySharedKey -o tsv) \
       --location eastus
   ```

3. Deploy the container app referencing the image from ACR:

   ```bash
   az containerapp create \
       --name sahith-ai-bot \
       --resource-group sahith-ai-rg \
       --environment sahith-ai-env \
       --image sahithaiacr.azurecr.io/sahith-ai-bot:latest \
       --target-port 8000 \
       --ingress 'external' \
       --registry-server sahithaiacr.azurecr.io \
       --query properties.configuration.ingress.fqdn
   ```

   The last flag returns the public FQDN that Azure assigns (e.g., `https://sahith-ai-bot.greencliff-1234.eastus.azurecontainerap
ps.io`).

4. Update the container when you publish a new image:

   ```bash
   az containerapp update \
       --name sahith-ai-bot \
       --resource-group sahith-ai-rg \
       --image sahithaiacr.azurecr.io/sahith-ai-bot:<new-tag>
   ```

---

## 4. Environment variables

The container honors the following variables (all optional):

| Variable | Description | Default |
| --- | --- | --- |
| `UVICORN_HOST` | Host/interface uvicorn listens on. | `0.0.0.0` |
| `UVICORN_PORT` | Port exposed by uvicorn. | `8000` |
| `UVICORN_WORKERS` | Number of worker processes. | `1` |
| `UVICORN_RELOAD` | Enable live reload (dev only). | `false` |

If you switch to PostgreSQL or Cosmos DB later, expose `DATABASE_URL` and update `app/database.py` to consume it. The Dockerfile
and compose setup already mount `/app/data` so SQLite survives container restarts.
