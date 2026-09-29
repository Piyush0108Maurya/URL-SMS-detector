# PhishGuard Edge: On-Device Phishing Detector for Snapdragon

PhishGuard Edge is a lightweight, machine learning-based phishing URL and SMS detector optimized for on-device inference using Qualcomm Snapdragon NPUs. By evaluating sequences directly on the device hardware, nothing is sent to the cloud, ensuring total privacy and making it highly relevant for security-conscious or offline environments.

## Results

| Metric | Value |
|--------|-------|
| Test Accuracy | 98.08% |
| Precision | 98.51% |
| Recall | 97.64% |
| F1 Score | 98.07% |

### Snapdragon X Elite Benchmark (Qualcomm AI Hub)

- **Inference Latency**: 2.008 ms
- **Peak Inference Memory**: ~156.5 MB (164,106,240 bytes)
- **Hardware Execution**: 246 NPU / 1 CPU ops
- **AI Hub Job**: [View on Qualcomm AI Hub](https://workbench.aihub.qualcomm.com/jobs/jgol7z41g/)

## Tech Stack

- **DistilBERT**: Base sequence classification model.
- **Qualcomm AI Hub**: Used for compiling and quantizing the model to run on the Snapdragon NPU.
- **FastAPI**: Lightweight local Python backend.
- **React**: Modern frontend interface for single and batch URL scanning.

## Known Limitations

The model performs exceptionally well on URLs that include a path component, as safe examples in the training dataset almost universally included one. However, bare root-domain lookups (e.g., `amazon.in` or `github.com` without trailing paths) can sometimes be misclassified as phishing. This is an artifact of a training-data coverage gap rather than a structural bug. 

*Future Work: Expand the safe-class coverage in the training set using a comprehensive domain popularity list to properly teach the model to accept bare root domains.*

## Project Structure

- `/data`: Contains raw datasets and data preparation scripts.
- `/model`: Scripts for fine-tuning the DistilBERT model and AI Hub compilation logic.
- `/backend`: FastAPI server handling inference and exposing REST endpoints.
- `/frontend`: React + Vite application for the user interface.
- `/docs`: Performance benchmarks, metrics, and documentation.

## Setup

> **Note**: This repository uses Git LFS (Large File Storage) for model files. Ensure you have [Git LFS](https://git-lfs.com/) installed and run `git lfs install` before cloning to retrieve the `model/phishing.onnx` file properly.

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure Qualcomm AI Hub (required for export and compile):
   Create a `.env` file based on `.env.example` with your AI Hub API token, and run the following command to generate the required config file (`~/.qai_hub/client.ini`):
   ```bash
   qai-hub configure --api_token <your_token_here>
   ```

## Demo App

The repository includes a demo application to run the phishing detector locally.

### Backend (FastAPI)
Start the backend server from the root directory:
```bash
venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend (React + Vite)
In a new terminal, install dependencies and start the dev server:
```bash
cd frontend
npm install
npm run dev
```
