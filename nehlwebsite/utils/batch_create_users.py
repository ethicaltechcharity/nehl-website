import csv
import datetime
import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

from clubs.models import Club, Member, ClubManagementPosition

User = get_user_model()

file = 'import.csv'

data = csv.reader(open(file), delimiter=",")
for row in data:
    try:
        uid = User.objects.get(username=row[5])
    except:
        user = User()
        user.password = make_password("4EVhHfXLu5kQjWNTTEV0")
        user.is_superuser = False
        user.username = row[5]
        user.email = row[5]
        user.first_name = row[2]
        user.last_name = row[3]
        user.is_staff = False
        user.is_active = True
        user.date_joined = datetime.datetime.now()
        user.save()
        club = Club.objects.get(pk=int(re.sub('[^0-9]', '', row[0])))
        member = Member()
        member.club = club
        member.date_of_birth = datetime.date.today()
        member.user_id = user.id
        member.registration_date = datetime.date.today()
        member.save()
        position = ClubManagementPosition()
        position.club = club
        position.type = row[1]
        position.holder_id = member.id
        position.save()

