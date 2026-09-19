from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment, Instructor, Tag
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = "Mintaadatok betöltése az online tanfolyam adatbázisba"

    def handle(self, *args, **options):
        if Course.objects.exists():
            self.stdout.write(self.style.WARNING("Az adatbázis már tartalmaz kurzusokat. A duplikációk elkerülése miatt a betöltés megszakítva."))
            return

        user, _ = User.objects.get_or_create(username="admin", defaults={"is_superuser": True, "is_staff": True})
        if not user.password:
            user.set_password("admin123")
            user.save()

        inst1 = Instructor.objects.create(name="Tóth Gábor", bio="Tapasztalt backend fejlesztő", birth_year=1980)
        inst2 = Instructor.objects.create(name="Kovács Anna", bio="Frontend specialista", birth_year=1990)
        inst3 = Instructor.objects.create(name="Nagy Péter", bio="Adattudós", birth_year=1985)

        tag1 = Tag.objects.create(name="Python", description="Python nyelv backendre")
        tag2 = Tag.objects.create(name="Web", description="Webfejlesztés")

        c1 = Course.objects.create(
            title="Python Mesterkurzus", slug="python-mesterkurzus", description="Minden, ami Python.",
            price=15000, published_year=2026, is_published=True, instructor=inst1
        )
        c1.tags.add(tag1, tag2)

        c2 = Course.objects.create(
            title="React Alapok", slug="react-alapok", description="Frontend fókusz",
            price=10000, published_year=2026, is_published=True, instructor=inst2
        )
        c2.tags.add(tag2)

        c3 = Course.objects.create(
            title="Adatbázisok", slug="adatbazisok", description="SQL és NoSQL",
            price=12000, published_year=2026, is_published=True, instructor=inst3
        )

        Enrollment.objects.create(
            course=c1, student_name="Kiss Béla", enrolled_at=date(2026, 1, 15), progress=50, created_by=user
        )
        Enrollment.objects.create(
            course=c2, student_name="Nagy Cecília", enrolled_at=date(2026, 2, 20), progress=100, completed_at=date(2026, 3, 20), created_by=user
        )

        self.stdout.write(self.style.SUCCESS("Mintaadatok sikeresen betöltve!"))