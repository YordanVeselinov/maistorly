# 🛠️ Maistorly

Maistorly is a web platform that connects customers with craftsmen and service providers. Users can create job requests, receive offers, and leave reviews after completing work.

---

## 🌐 Live Demo

👉 https://maristorly-fpdqa2bjbkeshcfu.polandcentral-01.azurewebsites.net

⚠️ **Note:** The application is hosted on Azure (free tier), which may result in slower response times or initial loading delays. Despite this, all functionalities work correctly.

---

## 🚀 Features

* 👤 User registration & authentication
* 🧑‍🔧 Craftsman profiles with service listings
* 📩 Job requests from customers
* 💰 Offers system between users
* ⭐ Reviews and ratings
* 🖼️ Image upload (Cloudinary integration)

---

## 🧱 Tech Stack

* **Backend:** Django 6 + Django REST Framework
* **Database:** PostgreSQL (Azure Database)
* **Task Queue:** Celery (optional)
* **Storage:** Cloudinary
* **Deployment:** Azure App Service (Linux)
* **Server:** Gunicorn

---

## ⚙️ Setup (Local Development)

```bash
git clone https://github.com/YordanVeselinov/maistorly.git
cd maistorly/backend

python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

pip install -r requirements.txt
```

Create a `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key

DB_ENGINE=django.db.backends.postgresql
DB_NAME=maistorly_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432

CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

Run:

```bash
python manage.py migrate
python manage.py runserver
```

---

## ☁️ Deployment Notes (Azure)

* Hosted on **Azure App Service (Linux)**
* Uses **Azure PostgreSQL Flexible Server**
* Static files handled with **WhiteNoise**
* Environment variables configured in Azure

---

## ⚠️ Known Limitations

* The app may load slowly due to Azure free-tier limitations
* Cold starts can delay the first request
* Celery is optional and not running in production

---

## 📌 Future Improvements

* Add caching (Redis)
* Improve performance
* Add async tasks in production
* Better UI/UX polish

---

## 👨‍💻 Author

**Yordan Veselinov**
