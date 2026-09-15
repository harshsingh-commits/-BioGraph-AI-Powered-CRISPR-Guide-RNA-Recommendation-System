# -BioGraph-AI-Powered-CRISPR-Guide-RNA-Recommendation-System
Developed a multi-agent AI system that analyzes gene sequences and recommends optimal CRISPR guide RNAs. Implemented PAM detection, guide RNA generation, off-target analysis, efficiency prediction, and risk assessment workflows. Built FastAPI APIs with JWT authentication, experiment tracking, and PostgreSQL integration. Added Docker deployment.
# 🧬 BioGraph

AI-Powered CRISPR Guide RNA Design & Off-Target Analysis System

BioGraph is a multi-agent bioinformatics platform built using LangGraph that automates CRISPR/Cas9 guide RNA discovery, safety analysis, ranking, and recommendation from FASTA gene sequences.

---

## 🚀 Features

- Gene Sequence Analysis
- PAM Site Detection
- Candidate gRNA Generation
- Off-Target Detection
- Efficiency Prediction
- Risk Assessment
- Explainable Guide Ranking
- Human Approval Workflow
- PDF Report Generation
- Experiment Tracking
- JWT Authentication & RBAC
- FastAPI Backend
- PostgreSQL Persistence
- Docker Deployment
- Prometheus & Grafana Monitoring

---

## 🏗 Architecture

FASTA Upload
↓
Gene Analyzer
↓
PAM Finder
↓
gRNA Generator
↓
Off-Target Detector
↓
Efficiency Predictor
↓
Risk Assessor
↓
Ranking Engine
↓
Human Approval
↓
Report Generator

---

## 🧠 Tech Stack

### AI & Workflow

- LangGraph
- Python

### Bioinformatics

- BioPython
- Bowtie2 (Optional)

### Frontend

- Streamlit

### Backend

- FastAPI
- JWT Authentication
- RBAC

### Database

- PostgreSQL
- SQLAlchemy

### Monitoring

- Prometheus
- Grafana

### DevOps

- Docker
- GitHub Actions

---

## 📊 Example Workflow

Upload a FASTA file:

```fasta
>BRCA1
ATCGATCGATCG...
