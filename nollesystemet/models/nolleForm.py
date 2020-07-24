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
            errors = self.validate_question_info(question_info)
            if errors:
                raise SyntaxError('Error in loading %s. Errors: %s' % (DynamicNolleFormQuestion, ", ".join(errors)))

            self.number_label = question_info['number_label']
            self.title = question_info['title']
            self.question_type = self.QuestionType.__getattr__(question_info['question_type'])
            self.save()

            if self.question_type != self.QuestionType.TEXT:
                for answer in question_info['answers']:
                    DynamicNolleFormQuestionAnswer(question=self, value=answer).save()

    @staticmethod
    def validate_question_info(question_info):
        error_messages = []
        for key in ['number_label', 'title', 'question_type']:
            if key not in question_info:
                error_messages.append("%s missing." % key)

        if question_info['question_type'] not in DynamicNolleFormQuestion.QuestionType.names:
            error_messages.append("question_type %s is not a valid question type. Alternatives are: %s." %
                              (question_info['question_type'],
                               ", ".join(DynamicNolleFormQuestion.QuestionType.names))
                              )

        question_type = DynamicNolleFormQuestion.QuestionType.__getattr__(question_info['question_type'])
        if question_type != DynamicNolleFormQuestion.QuestionType.TEXT:
            if 'answers' not in question_info:
                error_messages.append("%s missing." % key)

        return error_messages

    @staticmethod
    def validate_questions_from_dict(questions_info_dict):
        error_messages = []
        if 'dynamic_questions' in questions_info_dict:
            for i, question_info in enumerate(questions_info_dict['dynamic_questions']):
                question_errors = DynamicNolleFormQuestion.validate_question_info(question_info)
                if error_messages:
                    error_messages.append("Errors in question number %d: %s." % (i, ", ".join(question_errors)))
        else:
            error_messages.append("'dynamic_questions' not found in dictionary root.")

        return error_messages

    @staticmethod
    def set_questions_from_dict(questions_info_dict):
        if not DynamicNolleFormQuestion.validate_questions_from_dict(questions_info_dict):
            DynamicNolleFormQuestion.objects.all().delete()
            for question_info in questions_info_dict['dynamic_questions']:
                DynamicNolleFormQuestion(question_info=question_info)
        else:
            raise SyntaxError("Error in parsing dynamic_questions")


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
    contact_relation = models.CharField(max_length=200, choices=[(val, val) for val in
                                                                 ['Mamma', 'Pappa', 'Bror', 'Syster', 'Släkting',
                                                                  'Vän']])
    contact_phone_number = models.CharField(max_length=20)

    food_preference = models.TextField(blank=True)
    other = models.TextField(blank=True)

    about_the_form = models.CharField(max_length=200, choices=[(val, val) for val in [
        'Toppen!',
        'Bra',
        'Dåligt',
        'Sämst'
    ]])

    dynamic_answers = models.ManyToManyField(DynamicNolleFormQuestionAnswer, editable=False)

    class Meta:
        permissions = [
            ("edit_nolleForm", "Can edit the nolleForm form"),
        ]

    @staticmethod
    def can_fill_out(observing_user: UserProfile):
        if not observing_user.is_nollan():
            return False  # User is not NOLLAN.
        return True
