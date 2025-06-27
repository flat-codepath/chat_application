# 💬 Django WebSocket Chat App

A real-time chat application built with **Django**, **Channels (WebSockets)**, and **Bootstrap 5**.  
It supports **one-on-one messaging**, **image & file sharing**, and **replying to messages** — with a UI inspired by WhatsApp and Instagram chat interfaces.

> 🏢 **This project was developed as part of a technical assignment for [Gisfy Private Limited, Hyderabad](https://www.gisfy.com/)**.
---
## ✨ Features
- 🔐 User authentication (Login, Register, Logout)
- 💬 One-to-one real-time chat via WebSockets
- 📎 Image & file upload with previews
- 📲 Mobile-responsive UI using Bootstrap 5
- 🕐 Timestamps on messages
- ↩️ Reply to individual messages
- ✅ Clean and interactive UI (WhatsApp-style)

---

## 🛠️ Tech Stack

- Python 3.11+
- Django 4.x
- Django Channels (WebSockets)
- Bootstrap 5
- SQLite3 (or switch to PostgreSQL easily)

---

## 📦 Installation

### 1. Clone the repo
```bash
git clone https://github.com/your-username/django-chat-app.git
cd django-chat-app

## Create and activate virtual environment

python -m venv venv
source venv/bin/activate

##Install dependencies
pip install -r requirements.txt

 ##Apply migrations
python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser

##Run the development server
python manage.py runserver

 ##Run Daphne for WebSockets (optional but recommended)
daphne chatproject.asgi:application
