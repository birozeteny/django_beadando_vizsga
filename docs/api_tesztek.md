# API tesztek (curl / Postman)

### 1. Token kérése
Egy meglévő felhasználó hitelesítése az API-hoz.
```bash
curl -X POST [http://127.0.0.1:8000/api/token/](http://127.0.0.1:8000/api/token/) \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
```
*(A válaszként kapott "access" kulcs lesz a bearer tokenünk)*

### 2. Tanfolyamok listázása és keresése (Publikus)
Keresés azokra a kurzusokra, amiknek a nevében vagy a leírásában szerepel a "React" szó.
```bash
curl -X GET "[http://127.0.0.1:8000/api/courses/?search=React](http://127.0.0.1:8000/api/courses/?search=React)"
```

### 3. Új jelentkezés létrehozása (Védett)
A jelentkezéseket csak bejelentkezett felhasználók hozhatják létre, ekkor a `created_by` automatikusan a tokent küldő felhasználó lesz.
```bash
curl -X POST [http://127.0.0.1:8000/api/enrollments/](http://127.0.0.1:8000/api/enrollments/) \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>" \
     -d '{
           "course_id": 1,
           "student_name": "Kovács István",
           "enrolled_at": "2026-09-19"
         }'
```