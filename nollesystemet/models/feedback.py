from django.db import models

from .misc import IntegerChoices
from .user import UserProfile


class FeedbackTarget(IntegerChoices):
    """
    Enum target for status of a happening.
    """
    MOTTAGNINGEN = 1, "Fysiksektionens mottagning",
    THS = 2, "Mottagningen i allmänhet (Kåren)"
    SYSTEM = 3, "nØllesystemet"


class FeedbackObserver(models.Model):
    class Meta:
        verbose_name = 'Feedbackprenumerant'
        verbose_name_plural = 'Feedbackprenumeranter'
        unique_together = ('email', 'target')

    email = models.EmailField(blank=False, null=False)
    target = models.PositiveSmallIntegerField(choices=FeedbackTarget.choices, blank=False, null=False)

    def notify_of_feedback(self, feedback):
        if self.send_email_of_feedback(feedback):
            self.received_feedbacks.add(feedback)

    def send_email_of_feedback(self, feedback):
        pass


class Feedback(models.Model):
    """
    Model representing a filled out feedback form.
    """
    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'

    timestamp = models.DateTimeField(auto_created=True, editable=False)

    target = models.PositiveSmallIntegerField(choices=FeedbackTarget.choices, blank=False, null=False)

    anonymous = models.BooleanField(blank=False, null=False, default=False)

    user = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)
    external_name = models.CharField(max_length=100, blank=True, null=True)
    external_email = models.EmailField(blank=True, null=True)

    feedback = models.TextField(blank=False, null=False)

    notified_observers = models.ManyToManyField(FeedbackObserver, related_name="received_feedbacks", editable=False)

    @property
    def name(self):
        return self.user.name if self.user else self.external_name

    @property
    def email(self):
        return self.user.email if self.user else self.external_email

    @property
    def all_observers_notified(self):
        return all(
            [matchingObserver in self.notified_observers.all()
             for matchingObserver in FeedbackObserver.objects.filter(target=self.target)]
        )

    def notify_remaining_observers(self):
        non_notified_observers = [matchingObserver
                                  for matchingObserver in FeedbackObserver.objects.filter(target=self.target)
                                  if matchingObserver not in self.notified_observers.all()]

        for observer in non_notified_observers:
            observer.notify_of_feedback(self)