from django.core.management import BaseCommand

from catalog.models import Lesson, Module, Content


class Command(BaseCommand):
    help = 'Migrate data from modules to lessons'

    def handle(self, *args, **kwargs):
        modules = Module.objects.all()
        for module in modules:
            lessons = Lesson.objects.create(module=module, title=f"Lesson for {module.title}")

            Content.objects.filter(module=module).update(lesson=lessons)

        self.stdout.write(self.style.SUCCESS('Successfully migrated content to lesson'))
