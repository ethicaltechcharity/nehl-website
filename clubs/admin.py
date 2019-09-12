from django.contrib import admin
from clubs.models import *

# Register your models here.

admin.site.register([Club, Member, ClubManagementPosition, TransferRequest])

