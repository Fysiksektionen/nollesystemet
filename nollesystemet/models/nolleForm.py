from django.db import models
from django.dispatch import receiver

from .misc import validate_no_emoji
from .user import UserProfile


class DynamicNolleFormQuestion(models.Model):
    """ Model for a dynamic question of the NolleForm. Stores info only on the question itself, not any answers. """

    class QuestionType(models.IntegerChoices):
        """ Enum class of different question options """
        RADIO = 1, 'Single choice'
        CHECK = 2, 'Multiple choice'
        TEXT = 3, 'Text input'

    class Meta:
        verbose_name = 'nØlleformulärsfråga'
        verbose_name_plural = 'nØlleformulärsfrågor'

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
                    if isinstance(answer, dict):
                        DynamicNolleFormQuestionAnswer(question=self, value=answer['value'],
                                                       group=answer['group']).save()
                    elif isinstance(answer, str):
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
        if error_messages:
            return error_messages
        else:
            question_type = DynamicNolleFormQuestion.QuestionType.__getattr__(question_info['question_type'])
            if question_type != DynamicNolleFormQuestion.QuestionType.TEXT:
                if 'answers' not in question_info:
                    error_messages.append("answers missing.")
                else:
                    for answer_info in question_info['answers']:
                        if isinstance(answer_info, dict):
                            for key in ['value', 'group']:
                                if key not in answer_info:
                                    error_messages.append("'%s' missing in answer." % key)
                        elif not isinstance(answer_info, str):
                            error_messages.append("Wrong answer data type.")

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

    question = models.ForeignKey(DynamicNolleFormQuestion, models.CASCADE, null=False, blank=False, validators=[validate_no_emoji])
    value = models.CharField(max_length=400, validators=[validate_no_emoji])
    group = models.CharField(max_length=400, blank=True, null=True, validators=[validate_no_emoji])

    class Meta:
        unique_together = [('question', 'value'), ('question', 'group')]
        verbose_name = 'Svar till nØlleformulärsfråga'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.value)


class NolleFormAnswer(models.Model):
    """
    Model representing answer to the NolleForm. Contains hard-coded answer fields and a ManyToMany field storing
    all dynamic answers.
    """

    user = models.OneToOneField(UserProfile,
                                on_delete=models.CASCADE,
                                limit_choices_to={'user_type__is': UserProfile.UserType.NOLLAN},
                                editable=False)

    first_name = models.CharField(max_length=50, validators=[validate_no_emoji])
    last_name = models.CharField(max_length=50, validators=[validate_no_emoji])

    age = models.PositiveSmallIntegerField()
    age_feeling = models.PositiveSmallIntegerField(blank=True, null=True)

    home_address = models.CharField(max_length=400, validators=[validate_no_emoji])
    phone_number = models.CharField(max_length=30, validators=[validate_no_emoji])

    contact_name = models.CharField(max_length=100, validators=[validate_no_emoji])
    contact_relation = models.CharField(max_length=200, choices=[(val, val) for val in
                                                                 ['Förälder', 'Syskon', 'Släkting', 'Vän']])
    contact_phone_number = models.CharField(max_length=30, validators=[validate_no_emoji])

    food_preference = models.TextField(blank=True, validators=[validate_no_emoji])
    can_photograph = models.BooleanField()

    other = models.TextField(blank=True, validators=[validate_no_emoji])

    about_the_form = models.CharField(max_length=200, choices=[(val, val) for val in
                                                               ['Askalas!', 'Dunder', 'Lagom bra', 'Risigt']])

    dynamic_answers = models.ManyToManyField(DynamicNolleFormQuestionAnswer, editable=False)

    class Meta:
        permissions = [
            ("edit_nolleForm", "Can edit the nolleForm form"),
        ]
        verbose_name = 'nØlleformulärssvar'
        verbose_name_plural = verbose_name


    @staticmethod
    def can_fill_out(observing_user: UserProfile):
        if not observing_user.is_nollan():
            return False  # User is not NOLLAN.
        return True

    def __str__(self):
        return "Formulärsvar: %s" % self.user.name

@receiver(models.signals.post_save, sender=NolleFormAnswer)
def update_user_profile_from_nolleForm(sender, instance, *args, **kwargs):
    """ Deletes auth_user of deleted UserProfile """
    common_fields = ['first_name', 'last_name', 'phone_number', 'food_preference']
    if instance:
        for field_name in common_fields:
            setattr(instance.user, field_name, getattr(instance, field_name))
        instance.user.save()
