from django.db import models
from django.db.models import Q
from .user import UserProfile


class QuestionType(models.TextChoices):
    RADIO = 'R', 'Single choice'
    CHECK = 'C', 'Multiple choice'
    TEXT = 'T', 'Text input'

class DynamicQuestion(models.Model):
    number_label = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=300)

    question_type = models.CharField(max_length=1, choices=QuestionType.choices)


class DynamicAnswer(models.Model):
    question = models.ForeignKey(DynamicQuestion, models.CASCADE, null=False, blank=False)
    value = models.TextField()


class NolleFormAnswer(models.Model):
    user = models.OneToOneField(UserProfile,
                                models.CASCADE,
                                limit_choices_to={'auth_user__user_group__name__is': 'nØllan'})

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nick_name = models.CharField(max_length=50, blank=True)

    age = models.PositiveSmallIntegerField()
    age_feeling = models.PositiveSmallIntegerField(blank=True)

    home_adress = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)

    contact_name = models.CharField(max_length=100)
    contact_relation = models.CharField(max_length=200, choices=[(val, val) for val in ['Mamma', 'Pappa', 'Bror', 'Syster', 'Släkting', 'Vän']])
    contact_phone_number = models.CharField(max_length=20)

    food_preference = models.TextField()
    other = models.CharField(max_length=400)

    about_the_form = models.CharField(max_length=200, choices=[(val, val) for val in [
        'Toppen!',
        'Bra',
        'Dåligt',
        'Sämst'
    ]])

    dynamic_answers = models.ManyToManyField(DynamicAnswer)

