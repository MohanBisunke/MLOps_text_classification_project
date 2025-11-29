# MLOps End-to-End Project – Text Classification APP 
**Fully Deployed on AWS EKS with MLflow (DAGSHub), DVC + S3, Docker, GitHub Actions CI/CD, Prometheus & Grafana**


## Project Overview
Production-grade MLOps pipeline that includes:
- Cookiecutter Data Science structure
- MLflow experiment tracking on DAGSHub
- DVC for data & model versioning (S3 backend)
- Flask inference API
- Docker container
- GitHub Actions → Amazon ECR → Amazon EKS
- Monitoring with Prometheus + Grafana


## Project Structure
```
mlops-text-mohan/
├── .dvc/
├── .github/workflows/ci-cd.yaml
├── data/
├── flask_app/
│   ├── app.py
│   ├── templates/
│   └── requirements.txt
├── src/
│   ├── data_ingestion.py
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── model_building.py
│   ├── model_evaluation.py
│   ├── register_model.py
│   ├── model/
│   └── logger/
├── tests/
├── scripts/
├── dvc.yaml
├── params.yaml
├── requirements.txt
├── Dockerfile
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
└── README.md
```


### Critical Windows Setup (Avoid Conflicts)
```powershell
# 1. Remove pip-installed AWS CLI (causes conflicts)
pip uninstall awscli -y

# 2. Install official AWS CLI v2 via MSI → https://aws.amazon.com/cli/
# 3. Add C:\Program Files\Amazon\AWSCLIV2\ to System PATH

# 4. Download kubectl v1.34.2
Invoke-WebRequest -Uri "https://dl.k8s.io/release/v1.34.2/bin/windows/amd64/kubectl.exe" -OutFile "kubectl.exe"
Move-Item .\kubectl.exe C:\Windows\System32\

# 5. Download eksctl v0.219.0
Invoke-WebRequest -Uri "https://github.com/weaveworks/eksctl/releases/download/v0.219.0/eksctl_Windows_amd64.zip" -OutFile "eksctl.zip"
Expand-Archive eksctl.zip .
Move-Item .\eksctl.exe C:\Windows\System32\

# Verify
aws --version
kubectl version --client
eksctl version
```

## Quick Start (Local Development)
```bash
# 1. Clone & setup
git clone ....<Github repo url>
cd project root folder

# 2. Create & activate conda env
conda create -n mlops-text python=3.10 -y
conda activate mlops-text

# 3. Install core tools
pip install -r requirements.txt
pip install dagshub mlflow "dvc[s3]" awscli flask

# 4. DVC + S3 remote 
dvc init
dvc remote add -d origin s3://mlops-text-mohan (S3 Bucket Name)
git add .dvc/config && git commit -m "DVC remote → S3"

# 5. Run full pipeline
dvc repro        # executes all stages + logs to MLflow (DAGSHub)
dvc push         # pushes data/models to S3

# 6. Test Flask app locally
cd flask_app
python app.py    # → http://127.0.0.1:5000
```

## Docker
```bash
# From project root
docker build -t mlops-text-mohan:latest .
docker run -p 5000:5000 -e DAGHUB_TOKEN=your_dagshub_token mlops-text-mohan:latest
```

## GitHub Actions CI/CD Secrets (Required)
Add these in repo → Settings → Secrets and variables → Actions:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION                → us-east-1
AWS_ACCOUNT_ID
ECR_REPOSITORY            → mlops-text-mohan
DAGHUB_TOKEN              → Your DAGSHub token
```

## EKS Cluster Creation (One-time)
```bash
eksctl create cluster \
  --name mlops-text-mohan \
  --region us-east-1 \
  --nodegroup-name mlops-text-nodes \
  --node-type t3.small \
  --nodes 1 \
  --nodes-min 1 \
  --nodes-max 1 \
  --managed
```

After creation:
```bash
aws eks update-kubeconfig --name mlops-text-mohan --region us-east-1
kubectl get nodes   # should show 1 node READY
```

## Deploy to EKS (via GitHub Actions)
```bash
kubectl apply -f deployment.yaml


kubectl get svc mlops-text-mohan-service
# Wait 2–4 mins → External IP appears
```

## EKS App endoint (Already closed):  
http://a3bf4ce5f2efe45b3bdd66833caa24e3-827010463.us-east-1.elb.amazonaws.com:5000/predict

## Monitoring Stack (EC2 Instances -- Already closed)
- **Prometheus** : http://34.229.65.183:9090  
  Scrapes metrics from Flask app (via `/metrics` endpoint)
- **Grafana v12.3.0**: http://3.238.94.39:3000  
  Login: `admin` / `admin` → Add Prometheus as data source → Import community dashboards (e.g., Flask Exporter, Node Exporter)

## Cleanup (Avoid Billing Surprises!)
```bash
# Delete Kubernetes resources
kubectl delete -f k8s/

# Delete EKS cluster
eksctl delete cluster --name mlops-text-mohan --region us-east-1

# Manually delete (AWS Console):
# → ECR repository (mlops-text-mohan)
# → S3 bucket (mlops-text-mohan-bucket)
# → EC2 instances (Prometheus & Grafana)
# → Security Groups, IAM roles/policies created
```