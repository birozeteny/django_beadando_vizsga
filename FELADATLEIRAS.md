# Feladatleírás – Online tanfolyam beadandó vizsga

**100 pont · 3 hét · Django 5 + DRF**

A starter fájlok tetején részletes docstring specifikáció van. Ez a dokumentum a pontozási elvárásokat foglalja össze.

---

## A – Projekt + DRF setup (6 pt)

- `manage.py`, `requirements.txt` (Django, djangorestframework, simplejwt, django-filter, psycopg2-binary)
- `courses` app + `courses/api/` csomag
- `rest_framework` az `INSTALLED_APPS`-ben
- Dual DB: SQLite default, `USE_POSTGRES=1` → PostgreSQL (`tanfolyam`)

---

## B – Modellek + migráció (12 pt)

| Modell | Kapcsolatok / mezők |
|--------|---------------------|
| `Instructor` | `name`, `bio`, `birth_year` |
| `Tag` | `name` (unique), `description` |
| `Course` | FK `instructor`, M2M `tags`, `title`, `slug` (unique), `description`, `price`, `published_year`, `is_published` |
| `Enrollment` | FK `course`, FK `created_by` (User), `student_name`, `enrolled_at`, `progress`, `completed_at` |

`makemigrations` + `migrate` fusson.

---

## C – Admin (6 pt)

Mind a 4 modell regisztrálva. Course-on `EnrollmentInline`, `filter_horizontal` a tags-re, search + list_filter.

---

## D – Serializers + nested (10 pt)

- Course: nested `instructor` (read) + `instructor_id` (write)
- Enrollment: nested `CourseMiniSerializer` + `course_id` (write)
- `created_by` StringRelatedField (read_only)
- Hibás POST → 400

---

## E – ViewSet + Router CRUD (16 pt)

`ModelViewSet` + `DefaultRouter` alatt `/api/`:

- `/api/instructors/`
- `/api/tags/`
- `/api/courses/`
- `/api/enrollments/`

Teljes CRUD, helyes státuszkódok (200 / 201 / 204 / 404).

---

## F – Queryset optimalizálás (4 pt)

- `CourseViewSet`: `select_related("instructor").prefetch_related("tags")`
- `EnrollmentViewSet`: `select_related("course", "created_by")`

---

## G – JWT auth (10 pt)

- `POST /api/token/` → `access` + `refresh`
- `POST /api/token/refresh/`
- `Authorization: Bearer <access>` a védett végpontokhoz
- `JWTAuthentication` (+ Session a browsable API-hoz)

---

## H – Permissions (12 pt)

- Globál: `IsAuthenticatedOrReadOnly`
- Enrollment: `IsAuthenticated` + `IsEnrollmentOwner` (csak a létrehozó módosíthat/törölhet)
- `perform_create` → `created_by=request.user`
- Nem bejelentkezett Enrollment írás → **401**

---

## I – Pagination + filter (10 pt)

- Globál: `PageNumberPagination`, `PAGE_SIZE = 5`
- Course lista válasz: `count`, `next`, `previous`, `results`
- Course: `filterset_fields`, `search_fields`, `ordering_fields` (lásd views docstring)
- Backends: `DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`

---

## J – Seed command (4 pt)

`python manage.py seed_courses` → ≥3 instructor, ≥2 tag, ≥3 course, ≥2 enrollment. Ha már van Course, ne duplikáljon.

---

## K – Diák API tesztek (6 pt)

`courses/tests/test_api.py` – legalább **3** zöld API teszt (auth 401, pagination, search/filter).

---

## L – README + docs (4 pt)

- README: telepítés, JWT példa, filter URL
- `docs/er_diagram.md`: ER váz (szöveges vagy mermaid)
- `docs/api_tesztek.md`: legalább 3 curl/Postman példa (token, lista, create)

---

## Tippek

1. Először modellek + migráció + admin
2. Serializers → ViewSetek → Router → `config/urls.py`
3. JWT + permission
4. Pagination / filter a settings + CourseViewSet-en
5. Seed + saját tesztek + README

Órai analóg: könyvtár projekt (`Author`↔`Instructor`, `Book`↔`Course`, `Category`↔`Tag`, `Loan`↔`Enrollment`).
