# Beadandó vizsga – Online tanfolyam REST API (Django + DRF)

Ez a projekt egy online tanfolyamkezelő rendszer REST API-ja, amely Django 5 és Django REST Framework alapokon nyugszik.

## Futtatás és telepítés helyben
1. Hozz létre egy virtuális környezetet és aktiváld:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Telepítsd a függőségeket:
   ```bash
   pip install -r requirements.txt
   ```
3. Futtasd a migrációkat és a seed scriptet (mintaadatokhoz):
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_courses
   ```
4. Indítsd el a szervert:
   ```bash
   python manage.py runserver
   ```

## Token kérése és használata (JWT)
Küldj egy POST kérést a `/api/token/` végpontra a felhasználónévvel és jelszóval. A kapott `access` tokent minden védett végpontnál be kell rakni a kérés fejlécébe:
`Authorization: Bearer <access_token>`

## Példa: Tanfolyamok listázása, keresése és szűrése
Az összes tanfolyam lapozva jelenik meg (oldalanként 5 elem).
- **Keresés (címben/leírásban):** `GET /api/courses/?search=Python`
- **Szűrés (oktató alapján):** `GET /api/courses/?instructor=1`
- **Rendezés (ár szerint):** `GET /api/courses/?ordering=-price`

## Fő API Végpontok
- `/api/courses/` (GET, POST, PATCH, DELETE) - Kurzusok kezelése
- `/api/instructors/` - Oktatók lekérdezése
- `/api/tags/` - Címkék
- `/api/enrollments/` - Jelentkezések (Csak bejelentkezve)