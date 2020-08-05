from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import get_template

from .misc import validate_no_emoji
from .happening import Happening, DrinkOption, ExtraOption
from .user import UserProfile
from .settings import HappeningSettings

class Registration(models.Model):
    """ Model representing a registration of a user to a happening. Contains information on options and alike. """

    happening = models.ForeignKey(Happening, on_delete=models.CASCADE, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, editable=False)
    food_preference = models.CharField(max_length=150, validators=[validate_no_emoji])
    drink_option = models.ForeignKey(DrinkOption, blank=True, null=True, on_delete=models.SET_NULL)
    extra_option = models.ManyToManyField(ExtraOption, blank=True)
    other = models.CharField(max_length=300, blank=True, validators=[validate_no_emoji])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    confirmed = models.BooleanField(editable=False, default=False)
    paid = models.BooleanField(editable=False, default=False)
    attended = models.BooleanField(editable=False, default=False)

    class Meta:
        permissions = [
            ("see_registration", "Can see any registration"),
            ("edit_registration", "Can edit any registration"),
        ]
        verbose_name = 'Anmälan'
        verbose_name_plural = 'Anmälningar'

    def __str__(self):
        try:
            return str(self.user) + " anmäld till " + str(self.happening)
        except:
            return super().__str__()

    def can_see(self, observing_user: UserProfile):
        if observing_user == self.user:
            return True
        if self.can_edit(observing_user):
            return True
        if self.user.is_responsible_forfadder(observing_user):
            return True
        return False

    @staticmethod
    def can_see_some(observing_user: UserProfile):
        """ :return Boolean indicating if observing_user has the right to see the registration of some user. """
        # If can see more than one user. Larger than 1 because all users can see their own profile
        return len([True for registration in Registration.objects.all() if registration.can_see(observing_user)]) > \
               len(Registration.objects.filter(user=observing_user))

    def can_edit(self, observing_user: UserProfile):
        if observing_user.has_perm('nollesystemet.edit_registration'):
            return True
        if self.happening.can_edit(observing_user):
            return True
        return False

    @staticmethod
    def can_edit_some(observing_user: UserProfile):
        """ :return Boolean indicating if observing_user has the right to see the registration of some user. """
        # If can see more than one user. Larger than 1 because all users can see their own profile
        return len([True for registration in Registration.objects.all()
                    if registration.can_edit(observing_user)]) > 0

    @property
    def base_price(self):
        return self.happening.get_baseprice(self)

    @property
    def drink_price(self):
        if self.drink_option:
            return self.drink_option.price
        else:
            return 0

    @property
    def extra_option_price(self):
        return sum([values['price'] for values in self.extra_option.values('price')])

    @property
    def pre_paid_price(self):
        if self.happening.include_drink_in_price:
            return self.base_price + self.extra_option_price + self.drink_price
        else:
            return self.base_price + self.extra_option_price

    @property
    def on_site_paid_price(self):
        if self.happening.include_drink_in_price:
            return None
        else:
            return self.drink_price

    @property
    def all_extra_options_str(self):
        return [str(extra_option) for extra_option in self.extra_option.all()]

    def send_confirmation_email(self):
        """ (!) Only call this post save to db. """
        self.save()

        subject_template = get_template('fadderiet/evenemang/bekraftelse_epost_amne.txt')
        plaintext = get_template('fadderiet/evenemang/bekraftelse_epost.txt')
        html = get_template('fadderiet/evenemang/bekraftelse_epost.html')

        happening_info = HappeningSettings.load()

        from nollesystemet.forms import RegistrationForm
        context = {
            'registration': self,
            'happening': self.happening,
            'user_profile': self.user,
            'form': RegistrationForm(instance=self),
            'payment_info_html': happening_info.payment_info_html,
            'payment_info_plain_text': happening_info.payment_info_plain_text,
        }

        from_email, to = None, str(self.user.email)
        subject = subject_template.render(context)
        text_content = plaintext.render(context)
        html_content = html.render(context)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        res = msg.send()
        if res == 1:
            self.confirmed = True
            self.save()
            return True
        else:
            return False

