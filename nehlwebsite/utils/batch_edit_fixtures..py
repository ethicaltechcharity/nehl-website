from fixtures.models import Fixture

import django

django.setup()

for fixture in Fixture.objects.all():
    print(fixture)
