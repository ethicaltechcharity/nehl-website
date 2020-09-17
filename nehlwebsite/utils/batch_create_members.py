import csv
import datetime
import re
import django
django.setup()

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

from clubs.models import Club, Member

User = get_user_model()

file = 'data/members-with-dob.csv'

data = csv.reader(open(file), delimiter=',')
for row in data:
    username = (row[0][0] + '.' + row[1]).lower()
    if row[2] == 'NULL':
        continue
    try:
        uid = User.objects.get(username=username)
    except:
        user = User()
        user.password = make_password("oHrGTUlrLHg8uwv5mMZ0")
        user.is_superuser = False
        user.username = username
        user.first_name = row[0]
        user.last_name = row[1]
        user.is_staff = False
        user.is_active = True
        if row[5] == 'NULL':
            user.date_joined = datetime.date.today()
        elif '/' in row[5]:
            user.date_joined = datetime.datetime.strptime(row[5], '%d/%m/%Y %H:%M')
        else:
            user.date_joined = datetime.datetime.strptime(row[5], 'Y%-%d-%d %H:%M:%S')
        club = Club.objects.get(pk=int(re.sub('[^0-9]', '', row[4])))
        member = Member()
        member.club = club
        if '/' in row[2]:
            member.date_of_birth = datetime.datetime.strptime(row[2], '%d/%m/%Y %H:%M')
        else:
            member.date_of_birth = datetime.datetime.strptime(row[2], 'Y%-%d-%d %H:%M:%S')
        if row[5] == 'NULL':
            member.registration_date = datetime.date.today()
        elif '/' in row[5]:
            member.registration_date = datetime.datetime.strptime(row[5], '%d/%m/%Y %H:%M')
        else:
            member.registration_date = datetime.datetime.strptime(row[5], 'Y%-%d-%d %H:%M:%S')
        user.save()
        member.user_id = user.id
        member.save()

