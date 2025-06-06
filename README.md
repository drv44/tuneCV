# TuneCV – AI-Powered Resume Analyzer

TuneCV is a full-stack web application that allows users to upload their resumes and receive instant, actionable feedback and upskilling suggestions powered by AI. The project consists of a **FastAPI** backend and a **Next.js/React** frontend.

---

## Features

- Upload your resume (PDF, DOCX)
- Get AI-powered feedback and suggestions
- View history of past uploads and details in a modal
- Modern, responsive UI with smooth tab navigation

---

## Project Structure

```
.
├── app/                # FastAPI backend
│   └── main.py         # Backend entry point
├── frontend/           # Next.js frontend
│   └── src/app/        # Main frontend app code
├── requirements.txt    # Python backend dependencies
└── README.md           # Project documentation
```

---

## Prerequisites

- **Node.js** (v18+ recommended)
- **Python** (v3.9+ recommended)
- **PostgreSQL** (or update DB settings as needed)

---

## Backend Setup (FastAPI)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Make a file `.env` and set your database and API keys.
     

3. **Run the backend server:**
   ```bash
   cd app
   uvicorn main:app --reload
   ```
   The API will be available at [http://localhost:8000](http://localhost:8000).

---

## Frontend Setup (Next.js)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```
   The app will be available at [http://localhost:3000](http://localhost:3000).

---

## Usage

- Open [http://localhost:3000](http://localhost:3000) in your browser.
- Click **Get Started** to upload a resume and receive feedback.
- Click **View Past Uploads** to see your upload history and view details in a modal.

---


## Technologies Used

- **Frontend:** Next.js, React, Tailwind CSS, Shadcn UI
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, LangChain, Google Generative AI

---


## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---
