from keyword import iskeyword
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .misc import validate_no_emoji


class Site(models.Model):
    """ Model representing a site an its content such as texts and images. """
    name = models.CharField(max_length=200, unique=True, primary_key=False, validators=[validate_no_emoji])
    # created_date = models.DateTimeField(auto_now_add=True)
    # modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sida'
        verbose_name_plural = 'Sidor'

    @staticmethod
    def get_site_or_none(site_name):
        """ Returns the site or None if not existing. """
        try:
            return Site.objects.get(name=site_name)
        except Site.DoesNotExist:
            return None

    @staticmethod
    def get_populated_site(site_name, texts=None, images=None, paragraph_lists=None, clear_redundant=False):
        """
        Method for getting a site with all the specified fields initiated.
        :param site_name: String with the name of the site.
        :param texts: Array of keys for the texts for this site.
        :param images: Array of keys for the images for this site.
        :param clear_redundant: Boolean telling if to remove obsolete texts and images from database.
        :return: A site with texts and images created.
        """

        try:
            site = Site.objects.get(name=site_name)
        except Site.DoesNotExist:
            site = Site(name=site_name)
            site.save()

        if texts is None:
            texts = []
        if images is None:
            images = []
        if paragraph_lists is None:
            paragraph_lists = []

        current_text_keys = SiteText.objects.filter(site=site).values_list('key', flat=True)
        current_image_keys = SiteImage.objects.filter(site=site).values_list('key', flat=True)
        current_paragraph_lists_keys = SiteParagraphList.objects.filter(site=site).values_list('key', flat=True)

        if clear_redundant:
            delete_text_keys = [text_key for text_key in current_text_keys if text_key not in texts]
            SiteText.objects.filter(key__in=delete_text_keys, site=site).delete()

        for text_key in [text_key for text_key in texts if text_key not in current_text_keys]:
            site_text = SiteText(key=text_key, site=site)
            try:
                site_text.full_clean()
            except ValidationError:
                raise ValidationError(
                    "SiteText with key '%s' of site '%s' failed to validate." % (text_key, str(site_text.site))
                )

            site_text.save()

        if clear_redundant:
            delete_image_keys = [image_key for image_key in current_image_keys if image_key not in images]
            SiteImage.objects.filter(key__in=delete_image_keys, site=site).delete()

        for image_key in [image_key for image_key in images if image_key not in current_image_keys]:
            site_image = SiteImage(key=image_key, site=site)
            try:
                site_image.full_clean()
            except ValidationError:
                raise ValidationError(
                    "SiteImage with key '%s' of site '%s' failed to validate." % (image_key, str(site_image.site))
                )

            site_image.save()

        if clear_redundant:
            delete_paragraph_lists_keys = [para_key for para_key in current_paragraph_lists_keys if para_key not in paragraph_lists]
            SiteParagraphList.objects.filter(key__in=delete_paragraph_lists_keys, site=site).delete()

        for para_key in [para_key for para_key in paragraph_lists if para_key not in current_paragraph_lists_keys]:
            site_paragraph_list = SiteParagraphList(key=para_key, site=site)
            try:
                site_paragraph_list.full_clean()
            except ValidationError:
                raise ValidationError(
                    "SiteImage with key '%s' of site '%s' failed to validate." % (para_key, str(site_paragraph_list.site))
                )

            site_paragraph_list.save()

        return site

    def __str__(self):
        return self.name


def validate_variable_name(value):
    if not value.isidentifier() or iskeyword(value):
        raise ValidationError(
            _('%(value)s is not a valid key. Use a valid variable name.'),
            params={'value': value},
        )


class SiteText(models.Model):
    """ Model representing a text on a site. """
    key = models.CharField(max_length=100, blank=False, null=False, validators=[validate_variable_name])
    text = models.TextField(null=False, blank=True, validators=[validate_no_emoji])
    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=False, null=False, related_name='texts')

    # created_date = models.DateTimeField(auto_now_add=True)
    # modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('key', 'site')
        verbose_name = 'Test'
        verbose_name_plural = 'Texter'

    def __str__(self):
        return '%s: %s' % (self.site.name, self.key)


class SiteImage(models.Model):
    """ Model representing an image on a site. """
    key = models.CharField(max_length=100, blank=False, null=False, validators=[validate_variable_name])
    image = models.ImageField(null=False, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=False, null=False, related_name='images')

    # created_date = models.DateTimeField(auto_now_add=True)
    # modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('key', 'site')
        verbose_name = 'Bild'
        verbose_name_plural = 'Bilder'

    def __str__(self):
        return '%s: %s' % (self.site.name, self.key)

class SiteParagraphList(models.Model):
    """ Model representing an ordered list of paragraphs on a site """
    key = models.CharField(max_length=100, blank=False, null=False, validators=[validate_variable_name])
    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=False, null=False, related_name='paragraph_lists')
    ascending_order = models.BooleanField(choices=[(True, "Stigande"), (False, "Avtagande")],
                                          default=True, verbose_name="Ordning")

    # created_date = models.DateTimeField(auto_now_add=True)
    # modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('key', 'site')
        verbose_name = 'Styckeslista'
        verbose_name_plural = 'Styckeslistor'

    def __str__(self):
        return '%s: %s' % (self.site.name, self.key)

class SiteParagraph(models.Model):
    """ Model representing a paragraph in a paragraph list. """
    order_num = models.PositiveSmallIntegerField(blank=False, null=False)
    paragraph_list = models.ForeignKey(SiteParagraphList, on_delete=models.CASCADE, blank=False, null=False, related_name='paragraphs')
    title = models.CharField(max_length=200, null=False, blank=True, validators=[validate_no_emoji])
    text = models.TextField(null=False, blank=True, validators=[validate_no_emoji])
    image = models.ImageField(null=False, blank=True)

    # created_date = models.DateTimeField(auto_now_add=True)
    # modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stycke'
        verbose_name_plural = 'Stycken'

    def __str__(self):
        return '%s: %s: %d' % (self.paragraph_list.site.name, self.paragraph_list.key, self.order_num)

