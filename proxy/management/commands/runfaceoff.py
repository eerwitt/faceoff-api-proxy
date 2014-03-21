from django.core.management.commands.runserver import Command as RunServerCommand

# This runs Face/Off in a way that forces it to start *before* first hit
# Not always needed, but helpful for environments that spawn lots of instances like Heroku

class Command(RunServerCommand):
    def run(self, *args, **options):
        from faceoff import urls
        super(Command, self).run(*args, **options)
