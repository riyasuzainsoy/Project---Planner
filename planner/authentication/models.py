from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
class Rolechoice(models.TextChoices):
    ADMIN = 'Admin','Admin'
    USER = 'Project Coordinator','Project Coordinator'
    DEVELOPER='Developer','Developer'
class TechChoice(models.TextChoices):
    BACKEND ='Backend Developer','Backend Developer'
    FRONTEND ='Frontend Developer','Frontend Developer'
    FULLSTACK = 'Fullstack Developer','Fullstack Developer'
    UI_UX ='UI_UX Developer','UI_UX Developer'
    TESTER = 'Software Tester','Software Tester'
class Profile(AbstractUser):
    role = models.CharField(max_length=20,choices=Rolechoice.choices)
    tech = models.CharField(max_length=20, choices=TechChoice.choices, blank=True)
    class Meta:
        verbose_name = 'Profiles'
        verbose_name_plural = 'Profiles'
    def __str__(self):
        return f'{self.first_name}-{self.tech}'
             