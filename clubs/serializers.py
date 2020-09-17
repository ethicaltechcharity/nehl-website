from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from clubs.models import Member


class MemberSerializer(ModelSerializer):
    text = serializers.SerializerMethodField('get_user')

    class Meta:
        model = Member
        exclude = []

    def get_user(self, obj):
        return obj.__str__()


class MemberPlusDOBSerializer(ModelSerializer):
    text = serializers.SerializerMethodField('get_user')

    class Meta:
        model = Member
        exclude = []

    def get_user(self, obj):
        return obj.__str__() + ' ' + obj.date_of_birth.__str__()
