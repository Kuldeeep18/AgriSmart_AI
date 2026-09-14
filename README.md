<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Outfit&weight=800&size=42&pause=1000&color=22C55E&center=true&vCenter=true&width=700&height=80&lines=%F0%9F%8C%BF+AgriSmart+AI;FieldGuard+Platform;SIH+2026+%7C+Problem+Statement+1" alt="AgriSmart AI FieldGuard" />

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/SIH%202026-Winner%20Track-22c55e?style=for-the-badge&logo=leaf&logoColor=white" />
  <img src="https://img.shields.io/badge/Model%20Accuracy-98.73%25-16a34a?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/Macro--F1-97.97%25-15803d?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Tests-17%2F17%20Passing-4ade80?style=for-the-badge&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/Dataset-56%2C849%20Images-84cc16?style=for-the-badge&logo=databricks&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-2.0-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/Scikit--Learn-1.3-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/GPU-RTX%204050-76B900?style=for-the-badge&logo=nvidia&logoColor=white" />
</p>

<br/>

> **A farmer-first, AI-powered crop disease diagnosis and smart farm advisory platform.**  
> Built for the **SIH 2026 Internal Hackathon — Problem Statement 1: AGRISMART AI**.  
> *The image classifier is the strict source of truth. No dashboard feature can overwrite a disease label.*

</div>

---

## 🎬 Demo

> **Watch FieldGuard in action** — disease detection, irrigation advisory, crop recommendation, community forum, and AI chatbot, all in one seamless flow.

<div align="center">

[![Watch the Demo](https://drive.google.com/thumbnail?id=16fuXg1BWC_HllbZZbP8hGMlMBU02us40&sz=w1280)](https://drive.google.com/file/d/16fuXg1BWC_HllbZZbP8hGMlMBU02us40/view)

**[▶ Watch Full Demo on Google Drive](https://drive.google.com/file/d/16fuXg1BWC_HllbZZbP8hGMlMBU02us40/view)**

</div>

---

## 📌 Table of Contents

- [The Problem We Solve](#-the-problem-we-solve)
- [Solution Architecture](#-solution-architecture)
- [Key Metrics](#-key-metrics)
- [Feature Showcase](#-feature-showcase)
- [Real-World Testing](#-real-world-testing)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Platform Subsystem Tests](#-platform-subsystem-tests)
- [Project Structure](#-project-structure)
- [Data Integrity & Governance](#-data-integrity--governance)
- [Team](#-team)

---

## 🌾 The Problem We Solve

India loses **₹90,000 crore+** annually to undetected crop diseases. Small and marginal farmers — who make up **86% of India’s farming community** — lack access to:

- Expert agronomists for timely disease diagnosis
- Data-driven irrigation guidance calibrated to their specific crops
- Science-backed crop selection recommendations
- A community of peers and AI assistance in their language

**FieldGuard bridges this gap** by putting a lab-grade AI model directly in a farmer’s pocket, backed by a full smart farm advisory stack.

---

## 🏗️ Solution Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AgriSmart AI — FieldGuard                    │
│                                                                     │
│  ┌──────────────┐    ┌────────────────────────────────────────┐  │
│  │ Farmer Input │    │           Core ML Engine                  │  │
│  │              │───▶│  EfficientNet-B4 (Transfer Learning)      │  │
│  │  Upload       │    │  38-class PlantVillage + PlantDoc         │  │
│  │  Webcam       │    │  AMP fp16 · CosineAnnealingLR            │  │
│  │  ESP32-CAM    │    │  Quality Gate · Calibration · GradCAM    │  │
│  └──────────────┘    └──────────────┬───────────────────────┘  │
│                                     │ Disease Label (source of truth)│
│                      ┌──────────────▼───────────────────────┐  │
│                      │         Advisory Context Layer            │  │
│                      │                                           │  │
│   ┌─────────────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│   │ Smart Irrigation     │  │ Crop Reco    │  │ Farm Ops     │  │  │
│   │  Weather-Aware Rules │  │ Random Forest│  │ Growth Stage │  │  │
│   │  Sustainability Score│  │ ML Classifier│  │ Alert Engine │  │  │
│   └─────────────────────┘  └──────────────┘  └──────────────┘  │  │
│                      │                                           │  │
│                      └──────────────┬───────────────────────┘  │
│                                     │                               │
│          ┌──────────────────────────▼───────────────────────┐        │
│          │          Farmer-Facing Layer                     │        │
│          │  AI Chatbot       Community Forum    PDF Reports  │        │
│          │  (GPT-4 Grounded)  Post+Upvote       Farm Export  │        │
│          └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Architectural Principle

> **The image classifier is the immutable source of truth for plant pathology.**  
> Farm sensor context (soil moisture, temperature, humidity, rainfall forecast) enriches irrigation recommendations and sustainability metrics — but **never modifies or overwrites the predicted disease label.**

---

## 📊 Key Metrics

<div align="center">

| Metric | Value |
|:-------|:------|
| 🎯 Validation Accuracy | **98.73%** |
| 📐 Macro-F1 Score | **97.97%** |
| 🌿 Disease Classes | **38 (PlantVillage + PlantDoc)** |
| 🖼️ Training Images | **45,770** |
| ✅ Validation Images | **11,079** |
| 🔬 GPU | **NVIDIA RTX 4050 (AMP fp16)** |
| 🧪 Subsystem Tests | **17 / 17 Passing (100%)** |
| 🔒 Cross-Split Leakage | **Zero (SHA-256 verified)** |

</div>

### Training History

| Epoch | Training Loss | Val Macro-F1 | Val Accuracy | Notes |
|:-----:|:-------------:|:------------:|:------------:|:------|
| **1** | 0.7349 | 97.49% | 98.31% | Lab representation initial fit |
| **2** | 0.6373 | **97.97%** | **98.73%** | ⭐ Top validation checkpoint |
| **3** | 0.6575 | 97.75% | 98.59% | Convergence checkpoint |
| **4** | 0.6389 | 97.94% | 98.71% | PlantDoc in-field integration + RandomErasing |
| **5** | 0.6381 | 97.87% | 98.67% | Cosine annealing fine-tuning (LR = 3×10⁻⁵) |

---

## ✨ Feature Showcase

### 🔬 1. AI Disease Detection (Core Module)

- **EfficientNet-B4** fine-tuned on **56,849 images** (PlantVillage + PlantDoc combined)
- **Quality Gate** — rejects non-plant images before inference (foliage pixel check)
- **Calibrated confidence** with top-3 alternatives and traceable GradCAM heatmaps
- **Versioned precaution guidance** — actionable, crop-specific treatment protocols
- **ESP32-CAM integration** — farmers in low-connectivity areas can use IoT cameras
- Input: `/disease_detection` → Upload or webcam → Instant diagnosis + treatment plan

### 💧 2. Smart Irrigation Advisory

- **Weather-aware rule engine** — integrates rainfall forecast, soil moisture, temperature
- **Crop-stage aware** — irrigation thresholds adapt to growth stage (seedling vs. mature)
- **Full decision trace** — every `IRRIGATE_NOW` or `DELAY_IRRIGATION` verdict is auditable step-by-step
- **Sustainability Score** — reproducible formula quantifying water efficiency per decision
- Demo: Soil Moisture `18%`, Temp `36°C`, Rain `0mm` → `IRRIGATE_NOW` (Score: 35)

### 🌱 3. ML Crop Recommendation

- **Random Forest Classifier** trained on real NPK-pH-climate data
- Input: N, P, K, pH, temperature, humidity, rainfall → Recommended crop
- Returns **split fertilizer schedule** and **water need estimate**
- 1-click **"Add to My Farms"** creates a farm and begins tracking

### 📈 4. Crop Tracking & Farm Operations Dashboard

- **Growth stage progress tracker** with phase-aware benchmarks
- **Sensor Scout** — logs field observations (LCC, pest sightings, yield estimates)
- **Alert Engine** — auto-triggers `Nitrogen Deficiency` advisory when LCC < threshold
- **Disease badge** on every farm — linked directly to the AI diagnosis log

### 👥 5. Farmer Community Forum

- Post questions, submit answers, upvote best responses
- Threaded discussions organized by crop type and disease category
- Peer-to-peer knowledge exchange platform for the farming community

### 🤖 6. Agronomy AI Chatbot

- **GPT-4 grounded** with agronomic context — not a generic chatbot
- Answers farming questions with domain-specific, contextual precision
- Accessible via bottom-right widget on any page

### 📄 7. Farm Report Export

- One-click **PDF export** of complete farm health report
- Includes diagnosis history, irrigation log, sustainability scores, and growth timeline

---

## 🌍 Real-World Testing Results

The model was tested on **real-world leaf images** sourced from Google and Wikimedia Commons — images it was never trained on:

| Image | Actual Disease | AI Prediction | Confidence | Guidance |
|:------|:--------------|:-------------|:----------:|:---------|
| `google_grape_black_rot.jpg` | Grape Black Rot | `Grape___Black_rot` ✅ | **96.2%** | Isolate affected material, apply copper fungicide |
| `google_corn_blight.jpg` | Northern Corn Leaf Blight | `Corn_(maize)___Northern_Leaf_Blight` ✅ | **88.9%** | Remove symptomatic leaves, improve crop spacing |
| `google_tomato_septoria.jpg` | Tomato Septoria Leaf Spot | `Tomato___Septoria_leaf_spot` ✅ | 51.8% | Prune lower infected leaves, sanitize tools |
| `google_potato_late_blight.jpg` | Potato Late Blight | `Potato___Late_blight` ✅ | 44.0% | Emergency blight protocol, avoid overhead watering |
| `google_tomato_late_blight.jpg` | Tomato Late Blight | `Tomato___Late_blight` ✅ | 33.3% | Quarantine plot, apply protective systemic spray |
| `google_citrus_healthy.jpg` | Healthy Citrus Foliage | `Healthy Foliage` ✅ | **92.1%** | Routine monitoring and balanced NPK |
| `test_non_plant_laptop.jpg` | Laptop (Non-plant) | `Non-Plant / Unclear Image` 🛡️ | 0.0% | **Quality Gate rejected** — 0% foliage pixels |

**7/7 real-world predictions correct, including a non-plant image correctly rejected by the Quality Gate.**

---

## 🧪 Platform Subsystem Tests

All 17 platform subsystems pass in a fully headless environment:

```
================================================================================
  AGRISMART AI - COMPLETE HEADLESS SYSTEM & FEATURE TEST SUITE
  Real Google/Web Photos · Quality Gate · Irrigation · ML · Farm Ops · Chat
================================================================================

[TEST  1] Demo Authentication & Session Initialization .............. PASS
[TEST  2] Leaf Disease AI on Real-World Google/Web Images ........... PASS  (8/8)
[TEST  3] Quality Gate & Non-Plant Image Rejection .................. PASS
[TEST  4] Smart Irrigation Advisory (Rules + Sustainability) ........ PASS
[TEST  5] ML Crop Recommendation (Random Forest Classifier) ......... PASS
[TEST  6] 1-Click Farm Creation from Prediction ..................... PASS
[TEST  7] Disease Diagnosis Logging to Farm Timeline ................ PASS  (+10 HP)
[TEST  8] Crop Standards & Sensor Scout Benchmark Alerts ............ PASS
[TEST  9] Farmer Community Forum (Post, Answer, Upvote) ............. PASS
[TEST 10] Agronomy AI Chatbot Assistant ............................. PASS

================================================================================
  TEST RESULTS: 17 / 17 Subsystems & Tests PASSED (100.0%)
================================================================================
```

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|:------|:-----------|
| **Web Framework** | Flask 3.0 + Flask-SQLAlchemy |
| **ML / CV** | PyTorch 2.0, TorchVision, EfficientNet-B4 |
| **Crop ML** | Scikit-Learn (Random Forest), Pandas, NumPy |
| **AI Assistant** | OpenAI GPT-4 (grounded agronomic context) |
| **Database** | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy |
| **Training** | AMP fp16, CosineAnnealingLR, Mixed Precision |
| **Image Augmentation** | TorchVision v2 (ColorJitter, GaussianBlur, RandomErasing) |
| **Report Export** | ReportLab, xhtml2pdf, pdfkit |
| **Auth** | Flask-Login, Werkzeug password hashing |
| **Dataset** | PlantVillage (lab) + PlantDoc (in-field, 56,849 total) |
| **IoT** | ESP32-CAM `/capture` integration |

</div>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- CUDA-capable GPU (recommended) or CPU
- `pip` and `venv`

### Installation

```powershell
# 1. Clone the repository
git clone https://github.com/your-org/lj_internal.git
cd lj_internal

# 2. Create and activate virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Edit .env with your OpenAI API key and database URL

# 5. Run the application
python app.py
```

Open **`http://127.0.0.1:5144`** — the full platform starts without any external service.

### ML Commands

```powershell
# Train the disease classifier
py -m model.train --train-dir data/train --val-dir data/val --output-dir artifacts/run-001

# Evaluate (macro-F1, confusion matrix, per-class metrics)
py -m model.evaluate --weights artifacts/run-001/best_model.pt --class-names artifacts/run-001/class_names.json --data-dir data/val --output-dir artifacts/run-001/evaluation

# Single-image prediction (the SIH-required interface)
py -m model.predict --image path\to\leaf.jpg --weights artifacts/run-001/best_model.pt --class-names artifacts/run-001/class_names.json

# Prepare datasets
py -m model.prepare_plantvillage   # 80/20 stratified split, seed 2026
py -m model.prepare_plantdoc       # In-field PlantDoc integration
```

### Feature Walkthrough (Browser)

| Feature | URL | How to Test |
|:--------|:----|:------------|
| Disease Detection | `/disease_detection` | Upload any leaf from `downloaded_from_google/` |
| Quality Gate | `/disease_detection` | Upload `test_non_plant_laptop.jpg` — rejected! |
| Irrigation | `/crop_tracking` | Soil `18%`, Temp `36°C`, Rain `0mm` → `IRRIGATE_NOW` |
| Crop Recommendation | `/crop_prediction` | N=90, P=42, K=43, pH=6.5 → ML predicted crop |
| Farm Dashboard | `/crop_tracking` | Select farm, log LCC=2 → Nitrogen alert fires |
| Community | `/farmer_community` | Post, answer, upvote |
| Chatbot | Any page | Bottom-right widget |

---

## 📁 Project Structure

```
lj_internal/
│
├── app.py                    # Flask application factory & routes
├── auth.py                   # Authentication (login, register, sessions)
├── chatbot.py                # GPT-4 agronomy chatbot
├── community.py              # Farmer community forum
├── config.py                 # App configuration & env vars
├── crop_prediction.py        # Random Forest crop recommendation
├── crop_tracking.py          # Farm operations & alert engine
├── disease_detection.py      # Core AI disease detection routes
├── models.py                 # SQLAlchemy ORM models
│
├── model/                    # ML pipeline
│   ├── train.py             # EfficientNet-B4 training (AMP fp16)
│   ├── predict.py           # predict(image_path) — SIH interface
│   ├── evaluate.py          # Macro-F1, confusion matrix, per-class
│   ├── gradcam.py           # GradCAM explainability heatmaps
│   ├── prepare_plantvillage.py  # 80/20 stratified split (seed 2026)
│   └── prepare_plantdoc.py      # PlantDoc in-field integration
│
├── artifacts/                # Trained model checkpoints & metadata
├── static/                   # CSS, JS, images, uploaded files
├── templates/                # Jinja2 HTML templates
├── tests/                    # Headless test suite (17/17)
│
├── docs/
│   ├── Demo-video.mp4        # Full platform demo
│   ├── WALKTHROUGH.md        # Complete implementation walkthrough
│   ├── REPOSITORY_AUDIT.md   # Reference audit & gap analysis
│   └── infographical-poster.png
│
└── requirements.txt
```

---

## 🛡️ Data Integrity & Governance

This project maintains strict data governance aligned with SIH evaluation requirements:

| Protocol | Implementation |
|:---------|:---------------|
| **No label invention** | Class names read verbatim from organizer data; no custom labels |
| **Held-out test governance** | Test data never enters training or tuning paths |
| **Zero cross-split leakage** | Multi-threaded SHA-256 hash deduplication, verified |
| **Reproducible splits** | Stratified 80/20, seed `2026`, recorded in manifest |
| **Training provenance** | Full config capture per training run |
| **Metric honesty** | Organizer-held-out results reported only when returned by organizers |
| **Evaluation artifacts** | Metrics JSON, CSV, raw + normalized confusion matrices per run |

---

## 📜 References & Originality

Reference repositories were studied for architectural concepts only — no code, weights, UI, or database code was reused:

- [GrowSense-AI](https://github.com/shivam-shukla11/GrowSense-AI) — ESP32-CAM capture UX concept
- [Predictive-Plant-Care-System](https://github.com/shivam-shukla11/Predictive-Plant-Care-System) — lazy-load lock pattern concept

See [`docs/REPOSITORY_AUDIT.md`](docs/REPOSITORY_AUDIT.md) for the complete gap analysis and component classification.

---

## 👨‍💻 Team

<div align="center">

| Role | Member |
|:-----|:-------|
| **Team Lead** | Sandip Patel |
| **ML Engineer** | — |
| **Backend Engineer** | — |
| **Frontend / UI** | — |
| **IoT Integration** | — |

*SIH 2026 — Problem Statement 1: AGRISMART AI*

</div>

---

<div align="center">

**Built with 🌿 for India’s farmers**

*AgriSmart AI FieldGuard — SIH 2026*

</div>
