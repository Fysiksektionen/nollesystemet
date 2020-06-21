from django.db import models
from .user import UserProfile

class DynamicNolleFormQuestion(models.Model):
    """ Model for a dynamic question of the NolleForm. Stores info only on the question itself, not any answers. """

    class QuestionType(models.IntegerChoices):
        """ Enum class of different question options """
        RADIO = 1, 'Single choice'
        CHECK = 2, 'Multiple choice'
        TEXT = 3, 'Text input'

    number_label = models.CharField(max_length=30, blank=False, unique=True, primary_key=False)
    title = models.CharField(max_length=150, blank=False, null=None, unique=True, primary_key=False)

    question_type = models.PositiveSmallIntegerField(choices=QuestionType.choices, blank=False, null=None)

    def __init__(self, *args, question_info=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question_info is not None:
            try:
                self.number_label = question_info['number_label']
                self.title = question_info['title']
                self.question_type = self.QuestionType.__getattr__(question_info['question_type'])
            except:
                raise Exception('Error in loading ' + str(__class__) + ' from file-data')

            self.save()

            if self.question_type != self.QuestionType.TEXT:
                for answer in question_info['answers']:
                    DynamicNolleFormQuestionAnswer(question=self, value=answer).save()


class DynamicNolleFormQuestionAnswer(models.Model):
    """
    Model representing an answer to a DynamicNolleFormQuestion. Can be created upon loading of NolleForm setup or when
    a question is of type TEXT and a new answer is given.
    """

    question = models.ForeignKey(DynamicNolleFormQuestion, models.CASCADE, null=False, blank=False)
    value = models.CharField(max_length=400)

    class Meta:
        unique_together = ('question', 'value')

    def __str__(self):
        return str(self.value)


class NolleFormAnswer(models.Model):
    """
    Model representing answer to the NolleForm. Contains hard-coded answer fields and a ManyToMany field storing
    all dynamic answers.
    """

    user = models.OneToOneField(UserProfile,
                                models.CASCADE,
                                limit_choices_to={'user_type__is': UserProfile.UserType.NOLLAN},
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

    dynamic_answers = models.ManyToManyField(DynamicNolleFormQuestionAnswer, editable=False)

    @staticmethod
    def can_fill_out(observing_user: UserProfile):
        if NolleFormAnswer.objects.exists(user=observing_user):
            return False    # There is already an answer of this user.
        if observing_user.user_type != UserProfile.UserType.NOLLAN:
            return False    # User is not NOLLAN.
        return True

    @staticmethod
    def can_see_answers(observing_user: UserProfile):
        if observing_user.has_perm('see_users') or observing_user.has_perm('edit_users'):
            return True
        else:
            return False
