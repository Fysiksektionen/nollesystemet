from django.db import models
from .user import UserProfile


class QuestionType(models.TextChoices):
    RADIO = 'R', 'Single choice'
    CHECK = 'C', 'Multiple choice'
    TEXT = 'T', 'Text input'

class DynamicQuestion(models.Model):
    number_label = models.CharField(max_length=30, blank=False, unique=True, primary_key=False)
    title = models.CharField(max_length=150, blank=False, null=None, unique=True, primary_key=False)

    question_type = models.CharField(max_length=1, choices=QuestionType.choices, blank=False, null=None)

    def __init__(self, *args, question_info=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question_info is not None:
            try:
                self.number_label = question_info['number_label']
                self.title = question_info['title']
                self.question_type = QuestionType.__getattr__(question_info['question_type'])
            except:
                raise Exception('Error in loading ' + str(__class__) + ' from file-data')

            self.save()

            if self.question_type != QuestionType.TEXT:
                for answer in question_info['answers']:
                    DynamicAnswer(question=self, value=answer).save()


class DynamicAnswer(models.Model):
    question = models.ForeignKey(DynamicQuestion, models.CASCADE, null=False, blank=False)
    value = models.CharField(max_length=400)

    class Meta:
        unique_together = ('question', 'value')

    def __str__(self):
        return str(self.value)


class NolleFormAnswer(models.Model):
    user = models.OneToOneField(UserProfile,
                                models.CASCADE,
                                # limit_choices_to={'auth_user__user_group__name__is': 'nØllan'},
                                editable=False)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nick_name = models.CharField(max_length=50, blank=True)

    age = models.PositiveSmallIntegerField()
    age_feeling = models.PositiveSmallIntegerField(blank=True)

    home_address = models.CharField(max_length=200)
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

    dynamic_answers = models.ManyToManyField(DynamicAnswer, editable=False)

