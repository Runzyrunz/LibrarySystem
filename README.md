# LibrarySystem
Database Systems - Library System Programming Project

## Project Structure
```
LibrarySystem/
├── library/          ← Django project config
├── app/              ← Main library application
│   ├── templates/    ← HTML templates
│   ├── models.py     ← ORM definitions
│   ├── views.py      ← Business logic
│   ├── urls.py       ← App-specific routes
├── db.sqlite3        ← SQLite database (auto-generated)
├── manage.py         ← Django management script
```

---

## Requirements
- Python 3.8+
- Django 4.x or 5.x

Install dependencies:
```bash
pip install django
```

---

## How to Set Up

1. **Clone the Project** (or unzip if downloaded)
```bash
cd LibrarySystem
```

2. **Create the migrations folder if it doesn't exist**
```bash
mkdir app\migrations
copy NUL app\migrations\__init__.py
```

3. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create Admin User** *(optional)*
```bash
python manage.py createsuperuser
```

5. **Run the Server**
```bash
python manage.py runserver
```

6. **Open in Browser**
```
http://127.0.0.1:8000/
```

---

## Admin Panel (optional)
Visit: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)  
Use your superuser login.

---
