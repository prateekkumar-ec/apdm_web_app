# AI Document & Multimedia Q&A Web App

A full-stack application to upload PDF, audio, or video files, process them with AI, and interact via a chatbot for Q&A, summarization, and timestamped media playback.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd apdm_web_app
```

---

### 2. Backend Setup

#### a. Environment Variables

Create a `.env` file in `backend/` with:

```
OPENAI_API_KEY=your_openai_key
MONGO_URI=mongodb://localhost:27017
DB_NAME=aidm_db
UPLOAD_DIR=uploads
VECTORSTORE_DIR=vectorstore
```

#### b. Python Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### c. Start Backend Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will run at `http://localhost:5173`.

---

## 📚 API Documentation

### **File Upload**

- **POST** `/upload`
	- Upload a PDF, audio, or video file.
	- **Body:** `multipart/form-data` with `file`
	- **Response:** `{ file_id, file_name, extension, message }`

### **Process File**

- **POST** `/process/{file_id}`
	- Process the uploaded file (extract text/transcribe).
	- **Response:** `{ file_id, message }`

### **Q&A / Chatbot**

- **POST** `/qa`
	- Ask a question about a processed file.
	- **Body:** `{ file_id, question }`
	- **Response:** `{ answer, timestamps }`
		- `timestamps` is a list of `{ text, start, end, score }` for audio/video.

### **List Uploaded Files**

- **GET** `/files`
	- Returns: `{ files: [ { file_id, original_name, file_type, uploaded_at, status } ] }`

### **Get File Details**

- **GET** `/files/{file_id}`
	- Returns file metadata and processing status.

### **Health Check**

- **GET** `/health`
	- Returns: `{ status: "ok" }`

### **Serve Uploaded Files**

- **GET** `/uploads/{filename}`
	- Serves the uploaded file for playback or download.

---

## 🧪 Backend Testing


Tests are in `backend/tests/` and use `pytest`.

### Run all tests:

```bash
cd backend
pytest
```

### Check 95% Test Coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=95 tests/
```

- Tests cover upload, processing, Q&A, file listing, and health check endpoints.
- Example: `test_upload.py` tests file upload, `test_qa.py` tests Q&A, etc.

---

## 🚀 Running the App

1. **Start MongoDB** (if not running):  
	 `mongod --dbpath <your_db_path>`

2. **Start Backend**:  
	 `cd backend && uvicorn app.main:app --reload`

3. **Start Frontend**:  
	 `cd frontend && npm install && npm run dev`

4. **Open** [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📝 Notes

- Requires OpenAI API key for AI features.
- Supports PDF, MP3, WAV, and MP4 files.
- All API endpoints are available at `http://localhost:8000`.
- Frontend and backend can be run independently for development.

---

Let me know if you want any more details or changes!