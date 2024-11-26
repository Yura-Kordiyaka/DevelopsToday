from rest_framework import serializers
from .models import SpyCat, Mission, Target
from rest_framework.exceptions import ValidationError
import requests
import logging
from django.conf import settings

class SpyCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpyCat
        fields = ['id', 'name', 'years_of_experience', 'breed', 'salary']

    def validate_breed(self, value):
        if not value:
            raise ValidationError("Breed name cannot be empty.")

        headers = {'x-api-key': settings.CAT_API_KEY}
        response = requests.get("https://api.thecatapi.com/v1/breeds", headers=headers)

        if response.status_code != 200:
            raise ValidationError(f"Failed to retrieve breed data: {response.status_code}")

        data = response.json()

        breed_exists = any(breed["name"].lower() == value.lower() for breed in data)

        if not breed_exists:
            raise ValidationError(f"The breed '{value}' is not valid.")

        return value

    def validate_salary(self, value):
        if value < 0:
            raise ValidationError("Salary cannot be less than zero.")
        return value

class SpyCatUpdateSerializer(SpyCatSerializer):
    class Meta(SpyCatSerializer.Meta):
        fields = ['salary']


class SpyCatAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpyCat
        fields = ['id']

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['id', 'name', 'country', 'notes', 'is_complete']

    def validate_notes(self, value):
        if self.instance and self.instance.is_complete:
            raise ValidationError("Cannot modify notes after the target is complete.")
        return value

class TargetCompleteSerializer(serializers.Serializer):
    target_id = serializers.PrimaryKeyRelatedField(queryset=Target.objects)

    class Meta:
        fields = ['target_id']

class TargetSerializerUpdateNote(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['notes']

class MissionSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True)

    class Meta:
        model = Mission
        fields = ['id', 'cat', 'is_completed', 'targets']

    def create(self, validated_data):
        targets_data = validated_data.pop('targets')
        mission = Mission.objects.create(**validated_data)
        for target_data in targets_data:
            Target.objects.create(mission=mission, **target_data)
        return mission

    def update(self, instance, validated_data):
        targets_data = validated_data.pop('targets')
        instance.is_completed = validated_data.get('is_completed', instance.is_completed)
        instance.save()


        for target_data in targets_data:
            target_id = target_data.get('id')
            if target_id:
                target = Target.objects.get(id=target_id)
                target.name = target_data.get('name', target.name)
                target.country = target_data.get('country', target.country)
                target.notes = target_data.get('notes', target.notes)
                target.is_complete = target_data.get('is_complete', target.is_complete)
                target.save()
            else:
                Target.objects.create(mission=instance, **target_data)
        return instance
