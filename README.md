# VisionKYC - AI-Powered Identity Verification

<div align="center">

**An eKYC (Electronic Know Your Customer) System Based on Computer Vision and Deep Learning**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)

</div>

---

## Overview

VisionKYC is a comprehensive AI-powered identity verification system that automates the Know Your Customer (KYC) process using advanced computer vision and deep learning techniques. The system captures identity documents (PAN cards), extracts information through OCR, verifies face liveness, and compares faces for fraud detection.

### Key Features

- **ID Card Processing**: Automatic detection and extraction of ID cards from images
- **OCR Engine**: Extract structured information from identity documents using EasyOCR
- **Face Detection & Verification**: Detect faces and extract embeddings for comparison
- **Liveness Detection**: Verify that the face in the document matches the live face capture
- **Database Management**: Store and retrieve user records with MySQL backend
- **Duplicate Detection**: Prevent duplicate registrations based on ID uniqueness
- **Web Interface**: User-friendly Streamlit-based dashboard for seamless interaction
- **Logging & Monitoring**: Comprehensive logging for audit trails and debugging

---

## Quick Start with Docker (recommended)

Everything (the app **and** MySQL) runs with one command. You only need
[Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + the Compose plugin).

```bash
# 1. open a terminal in the project folder (where docker-compose.yml is)
# 2. build and start everything
docker compose up --build
```

Then open **http://localhost:8501**.

- The first build takes ~10-20 minutes and downloads ~5 GB (PyTorch, TensorFlow and the
  face/OCR model weights are baked into the image). Later starts take seconds.
- Give Docker at least **4 GB RAM** (Docker Desktop -> Settings -> Resources).
- The MySQL table `users` is created automatically; no SQL setup is needed.

| Task | Command |
|------|---------|
| Start in background | `docker compose up -d` |
| Watch app logs | `docker compose logs -f app` |
| Stop | `docker compose down` |
| Stop **and delete all stored data** | `docker compose down -v` |
| Rebuild after code changes | `docker compose up --build` |
| Look at registered users | `docker compose exec db mysql -u ekyc_user -pekyc_password ekyc -e "select id,name,father_name,dob,id_type,create_time from users"` |

**Changing DB credentials:** copy `.env.example` to `.env`, edit it, then
`docker compose down -v && docker compose up --build` (the old DB volume keeps the old password).

**Try it out:** upload a PAN card image as the ID card and a clear selfie of the same person
as the face image. Sample PAN cards are in `data/01_raw_data/` (`pan_2.jpg`, `pan_1.jpg`, ...).

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│         Streamlit Web Interface              │
│  (UI for image upload and verification)      │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┬──────────────┐
       ▼                ▼              ▼
  ┌─────────┐    ┌──────────┐    ┌────────────┐
  │Preprocess│    │ OCR      │    │ Face       │
  │Engine    │    │ Engine   │    │ Verification│
  │(ID Card) │    │(EasyOCR) │    │(DeepFace)  │
  └────┬────┘    └──────┬───┘    └─────┬──────┘
       │                │              │
       └────────────┬───┴──────────────┘
                    ▼
         ┌──────────────────────┐
         │ Post-processing &    │
         │ Information Extraction│
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Database Operations  │
         │ (MySQL Storage)      │
         └──────────────────────┘
```

### Workflow

1. **User Input**: User uploads ID card image and live face image
2. **ID Card Processing**: 
   - Extract ID card region using contour detection
   - Preprocess image for better OCR accuracy
3. **Text Extraction**:
   - Use EasyOCR to extract text from ID card
   - Parse structured information (Name, ID, DOB, etc.)
4. **Face Verification**:
   - Detect and extract face from ID card
   - Compare with uploaded live face image
   - Generate face embeddings for future verification
5. **Database Storage**:
   - Check for duplicates
   - Store user record with embeddings and metadata

---

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL/MariaDB database
- CUDA 11.0+ (recommended for GPU acceleration)

### Setup Steps

1. **Clone the Repository**

```bash
git clone https://github.com/DecoderX108/VisionKYC-AI-Powered-Identity-Verification.git
cd VisionKYC-AI-Powered-Identity-Verification
```

2. **Create Virtual Environment**

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure the database connection**

The app reads its MySQL settings from environment variables (defaults in brackets):

```bash
export MYSQL_HOST=localhost      # [localhost]
export MYSQL_PORT=3306           # [3306]
export MYSQL_USER=root           # [root]
export MYSQL_PASSWORD=yourpass   # [empty]
export MYSQL_DATABASE=ekyc       # [ekyc]
# Windows PowerShell:  $env:MYSQL_HOST="localhost"  (same for the others)
```

Create the (empty) database once - the `users` table is created automatically by the app:

```sql
CREATE DATABASE ekyc;
```

No `.streamlit/secrets.toml` is needed any more. Use Python 3.10 (TensorFlow 2.15 does not
support 3.12+).

---

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

### User Workflow

1. **Select ID Type**: Choose between PAN or Aadhar card from sidebar
2. **Upload ID Card**: Upload image of the front of ID card
3. **Upload Face Image**: Upload a clear photo of your face
4. **Verification Process**: 
   - System extracts information from ID card
   - Compares face from ID with uploaded photo
   - Stores record if verification successful
5. **View Results**: Confirmation of registration and stored information

---

## Module Documentation

### Core Modules

#### `preprocess.py`
Handles image preprocessing and ID card detection:
- `read_image()`: Load and process image files
- `extract_id_card()`: Detect and crop ID card region
- `save_image()`: Save processed images

#### `ocr_engine.py`
Text extraction and OCR operations:
- `extract_text()`: Extract text from ID card using EasyOCR
- Integration with multiple OCR models

#### `postprocess.py`
Structured information extraction:
- `extract_information()`: Parse OCR text into structured fields
- Handles various ID card formats
- Regex-based field extraction

#### `face_verification.py`
Face detection and comparison:
- `detect_and_extract_face()`: Detect face regions using Haar Cascade
- `face_comparison()`: Compare two face images for similarity
- `get_face_embeddings()`: Generate face embeddings using DeepFace
- Uses multiple models: VGGFace, Facenet, OpenFace

#### `mysqldb_operations.py`
Database operations:
- `insert_records()`: Store user information and embeddings
- `fetch_records()`: Retrieve user records by criteria
- `check_duplicacy()`: Verify if user already exists

#### `db_operations.py`
Additional database utilities for SQLAlchemy integration

#### `app.py`
Main Streamlit application:
- Web interface and user interaction
- Orchestrates all modules
- Handles file uploads and display

---

## Configuration

Key configuration parameters in `config.yaml`:

| Parameter | Description | Default |
|-----------|-------------|----------|
| FACERECOG_MODEL | Face recognition model | deepface |
| HAARCASCADE_PATH | Haar Cascade classifier path (use `/` separators) | data/models/haarcascade_frontalface_default.xml |
| INTERMEDIATE_DIR | Temp directory for processing | data/02_intermediate_data |
| FACE_THRESHOLD | Similarity threshold (0-1) | 0.6 |

---

## Dependencies

Key Python packages:

- **Computer Vision**: OpenCV 4.9.0, scikit-image, PIL
- **Face Recognition**: DeepFace (TensorFlow 2.15). `face-recognition`/`dlib` is optional and not installed by default
- **OCR**: EasyOCR
- **Web Framework**: Streamlit 1.32.2
- **Database**: mysql-connector-python 9.0.0
- **ML/DL**: PyTorch 2.2.1, NumPy 1.24.4, SciPy 1.10.1

See `requirements.txt` for complete dependency list.

---

## Project Structure

```
VisionKYC-AI-Powered-Identity-Verification/
├── app.py                          # Main Streamlit application
├── config.yaml                     # Configuration file
├── requirements.txt                # Python dependencies
├── requirements_deepface.txt       # DeepFace specific requirements
├── Dockerfile                      # App image (CPU-only)
├── docker-compose.yml              # App + MySQL
├── .env.example                    # Optional DB credentials for docker compose
├── scripts/preload_models.py       # Downloads model weights at image build time
│
├── preprocess.py                   # Image preprocessing module
├── ocr_engine.py                   # OCR text extraction
├── postprocess.py                  # Information extraction
├── face_verification.py            # Face detection & verification
├── mysqldb_operations.py           # Database operations
├── db_operations.py                # SQLAlchemy operations
├── utils.py                        # Utility functions
│
├── data/
│   ├── 02_intermediate_data/       # Temporary processed images
│   └── models/                     # ML model files
│
├── logs/
│   └── ekyc_logs.log              # Application logs
│
├── notebooks/
│   └── test.ipynb                 # Testing and experimentation
│
└── ekyc.drawio                     # System architecture diagram
    ocr.drawio                      # OCR workflow diagram
```

---

## Performance & Limitations

### Performance Metrics

- **Face Detection Accuracy**: ~98% (Haar Cascade)
- **Face Comparison Threshold**: 0.6 (configurable)
- **OCR Accuracy**: ~85-95% depending on image quality
- **Processing Time**: 3-8 seconds per registration

### Current Limitations

- Requires clear, well-lit images for accurate OCR
- Face verification works best with frontal faces
- Supports PAN and Aadhar cards (extensible to other formats)
- MySQL dependency for data storage
- Single-user processing (can be parallelized)

---

## Future Improvements

- [ ] Support for multiple ID card types (Passport, License, Voter ID)
- [ ] Liveness detection for anti-spoofing
- [ ] Batch processing API endpoint
- [ ] Enhanced OCR with fine-tuning on Indian ID cards
- [ ] Microservices architecture for scalability
- [ ] GraphQL API for flexible data queries
- [ ] Redis caching for duplicate detection
- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Automated quality checks for images

---

## Security Considerations

⚠️ **Important**: This project handles sensitive personal information. Before production deployment:

- [ ] Implement encryption for stored embeddings
- [ ] Use HTTPS for all communications
- [ ] Implement proper authentication and authorization
- [ ] Add rate limiting for API endpoints
- [ ] Regular security audits and penetration testing
- [ ] Comply with GDPR, CCPA, and local regulations
- [ ] Implement proper access controls and logging
- [ ] Secure database credentials in environment variables

---

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Verify MySQL is running
   # Check the MYSQL_* environment variables (or .env for Docker)
   # Ensure database exists
   ```

2. **Face Detection Not Working**
   ```bash
   # Verify Haar Cascade XML file exists
   # Check image quality and lighting
   # Ensure face is clearly visible
   ```

3. **OCR Accuracy Issues**
   ```bash
   # Improve image quality (higher resolution)
   # Better lighting conditions
   # Ensure ID card is flat and straight
   ```

4. **Import Errors**
   ```bash
   # Reinstall requirements
   pip install --upgrade -r requirements.txt
   ```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

---

## Authors

- **Prasanna Sen Thakuri** — project lead
- **Shovit Kafle** — team member
- **Samyog Rajbhandari** — team member

---

## Acknowledgments

- OpenCV for computer vision capabilities
- DeepFace for face recognition models
- EasyOCR for text extraction
- Streamlit for web interface framework
- The open-source ML community

---

## Contact & Support

For issues, questions, or suggestions:

- Open an [issue](https://github.com/DecoderX108/VisionKYC-AI-Powered-Identity-Verification/issues)
- Contact: prasanna_25126469@sunway.edu.np

---

**Last Updated**: October 2026
