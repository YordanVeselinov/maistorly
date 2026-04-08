# Maistorly

Maistorly is a web platform that connects clients with craftsmen for home services and repairs.

The goal of the application is to provide a simple and reliable way for users to find professionals for tasks such as electrical work, plumbing, renovations, and more.

---

## 🚀 Features

### 👤 Authentication
- Custom user model
- Email-based login
- Registration and logout
- Role-based access using Django Groups:
  - Clients
  - Craftsmen

---

### 🧰 Job Requests
- Users can create job requests
- Each job contains:
  - Title
  - Description
  - Budget range
  - Preferred date
  - Location
- Users can:
  - View all jobs
  - View their own jobs
  - Edit and delete their jobs

---

### 🛠️ Offers System
- Craftsmen can apply to jobs
- Each offer includes:
  - Message
  - Proposed price
  - Estimated time
- Job owners can review offers

---

### 👷 Craftsmen Profiles
- Craftsmen can manage their profiles
- Profiles include:
  - Skills
  - Location
  - Description
- Users can browse craftsmen

---

### ⭐ Reviews
- Clients can leave reviews after a job is completed
- Includes rating and comment
- One review per job

---

### 🌐 Public & Private Access
- Public pages for anonymous users
- Private pages for authenticated users
- Dynamic navigation based on authentication

---

### 🔗 REST API
- Built with Django REST Framework
- Endpoints for:
  - Jobs
  - Craftsmen

---

### ⚙️ Async Tasks
- Celery used for background processing
- Example:
  - Sending notifications for new offers

---

## 🧱 Tech Stack

- Django
- Django REST Framework
- PostgreSQL
- Bootstrap 5
- Celery + Redis
- Docker

---

## 🗂️ Project Structure

- accounts – authentication and users
- services – categories and skills
- craftsmen – craftsmen profiles
- jobs – job requests and offers
- reviews – reviews and ratings

---

## ⚙️ Setup

### 1. Clone repository

```bash
git clone <your-repo-url>
cd maistorly
