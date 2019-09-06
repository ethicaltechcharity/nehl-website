from django.contrib import admin
from clubs.models import Club, Member

# Register your models here.

admin.site.register([Club, Member])

