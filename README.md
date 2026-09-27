# On-Device Phishing Detector for Snapdragon

This project is a machine learning-based phishing URL and SMS detector optimized for on-device inference.

## Setup

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
