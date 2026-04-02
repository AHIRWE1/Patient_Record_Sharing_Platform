# MediShare Rwanda - Integrated Patient Record Sharing Platform

A web-based platform that enables hospitals across Rwanda to securely register patients, manage medical records, and share patient data with other hospitals during transfers and referrals - with full audit logging and role-based access control.

---

## Problem It Solves

When a patient transfers between hospitals, the receiving facility has no access to their history. MediShare solves this by letting the originating hospital send a controlled share request; the receiving hospital approves it and can view the full medical record instantly, without duplicating data.

---

## Key Features

- **User Authentication** - Secure login with bcrypt-hashed passwords; three roles: Admin, Staff, Doctor
- **Role-Based Access Control (RBAC)** - Admins manage users; staff/doctors access records within their hospital
- **Patient Registration** - Register patients with name, date of birth, gender, and National ID
- **Medical Record Management** - Add diagnosis, treatment, lab tests, and clinical notes per patient
- **Inter-Hospital Record Sharing** - Send share requests to other hospitals; approve or reject incoming requests
- **Shared Record Viewer** - Approved hospitals get read-only access to a patient's full medical history
- **Dashboard** - Overview of patients, records, pending share requests, and recent activity
- **Audit Trail** - Every action (login, record creation, share approval) is logged with user and timestamp
- **About & Help Pages** - In-app guidance for all user roles

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.12, Flask 3.0              |
| ORM        | Flask-SQLAlchemy 3.1 (SQLAlchemy 2) |
| Database   | PostgreSQL via Neon (production)    |
| Database   | SQLite (local development)          |
| Auth       | Flask-Login + Flask-Bcrypt          |
| Frontend   | Bootstrap 5, Bootstrap Icons        |
| Deployment | Render + Neon                       |

---

## Installation - Step by Step

### 1. Clone the Repository

```bash
git clone https://github.com/AHIRWE1/Patient_Record_Sharing_Platform.git 
cd Patient_Record_Sharing_Platform
```

### 2. Create and Activate a Virtual Environment

```bash
# Create
python -m venv venv

# Activate - Windows
venv\Scripts\activate

# Activate - Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-long-random-secret-key
DATABASE_URL=your_neon_connection_string_here
```

- Leave `DATABASE_URL` out entirely to use SQLite locally (automatic fallback).
- Set `DATABASE_URL` to your Neon pooled connection string (including `?sslmode=require`) for PostgreSQL.

### 5. Run the Application

```bash
python run.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## Database Notes

| Environment | Database  | How it works                                                      |
|-------------|-----------|-------------------------------------------------------------------|
| Local dev   | SQLite    | Default - no setup needed. DB file created automatically.         |
| Production  | Neon (PG) | Set `DATABASE_URL` env var to your Neon pooled connection string. |

Tables are created automatically on first run via `db.create_all()`.

---

## Usage Guide

### 1. First-Time Setup
1. Go to `http://127.0.0.1:5000`
2. Click **Register Hospital** to create your hospital and an admin account.
3. Log in with your admin credentials.

### 2. Managing Users (Admin only)
1. From the dashboard sidebar, click **Manage Users**.
2. Click **Add User** to create staff or doctor accounts for your hospital.

### 3. Registering a Patient (Staff/Admin)
1. Click **Patients** in the sidebar.
2. Click **Register New Patient**.
3. Fill in Full Name, National ID, Date of Birth, and Gender.
4. Click **Register Patient**.

### 4. Adding a Medical Record (Staff/Doctor)
1. Click **Patients**, then click a patient's name.
2. Click **Add Medical Record**.
3. Fill in Diagnosis, Treatment, Lab Tests, and Clinical Notes.
4. Click **Save Record**.

### 5. Sharing Records with Another Hospital (Staff/Admin)
1. Click **Share Records** in the sidebar.
2. Select a patient and the target hospital, then click **Send Request**.
3. The receiving hospital must log in and approve the request.
4. Once approved, they can click **View Records** to see the patient's full history (read-only).

### 6. Viewing Audit Logs (Admin only)
1. Click **Audit Logs** in the sidebar.
2. See a full history of all actions taken within your hospital.

---

## Deployment

This project is deployed on **Render** with **Neon PostgreSQL**.

### Steps to Deploy on Render
1. Push your code to GitHub.
2. Create a new **Web Service** on [render.com](https://render.com) connected to your repo.
3. Set the following environment variables in Render's dashboard:
   - `SECRET_KEY` - a long random string
   - `DATABASE_URL` - your Neon pooled connection string
4. Set the **Start Command** to:
   ```
   gunicorn run:app
   ```
5. Deploy. Render will install dependencies from `requirements.txt` automatically.

---

## Links

| Resource            | URL                                                    |
|---------------------|--------------------------------------------------------|
| Live App            | _https://patient-record-sharing-platform-1.onrender.com_ |
| GitHub Repository   | _https://github.com/AHIRWE1/Patient_Record_Sharing_Platform.git_ |
| SRS Document        | _https://docs.google.com/document/d/1sZScFQKE1Ic_2PamM-1FCWVW_G2LmMmvMHkvS3hW_i0/edit?usp=sharing_ |
| Demo Video          | _https://youtu.be/V6VImEk5B2c_ |

---

## SRS Functional Requirements Coverage

| Requirement | Description                        | Status      |
|-------------|------------------------------------|-------------|
| FR1         | User Authentication (bcrypt)       | Implemented |
| FR2         | Patient Registration               | Implemented |
| FR3         | Record Retrieval & Search          | Implemented |
| FR4         | Medical Record Management          | Implemented |
| FR5         | Inter-Hospital Record Sharing      | Implemented |
| FR6         | Dashboard with stats & activity    | Implemented |
| FR7         | Audit Trail                        | Implemented |
| NFR1        | Security (RBAC, password hashing)  | Implemented |
| NFR2        | Performance (indexed queries)      | Implemented |
| NFR4        | Usability (Bootstrap responsive UI)| Implemented |
