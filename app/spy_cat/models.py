from django.db import models
from django.core.exceptions import ValidationError
import requests

class SpyCat(models.Model):
    name = models.CharField(max_length=100)
    years_of_experience = models.IntegerField()
    breed = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return self.name


class Mission(models.Model):
    cat = models.OneToOneField(SpyCat, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Mission {self.id} for {self.cat.name if self.cat else 'Unassigned'}"



class Target(models.Model):
    mission = models.ForeignKey(Mission, related_name='targets', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    is_complete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_complete and self.pk:
            original = Target.objects.get(pk=self.pk)
            if original.is_complete and original.notes != self.notes:
                raise ValidationError("Cannot modify notes after the target is complete.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Target {self.name} in {self.country}"
