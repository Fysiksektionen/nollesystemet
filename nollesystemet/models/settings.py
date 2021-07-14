from django.core.cache import cache
from django.db import models

class SingeltonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingeltonModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def __str__(self):
        if hasattr(self._meta, 'verbose_name'):
            return self._meta.verbose_name
        else:
            return type(self).__name__


class HappeningSettings(SingeltonModel):
    payment_info_html = models.TextField(blank=True, verbose_name="Betalningsinformation (HTML)")
    payment_info_plain_text = models.TextField(blank=True, verbose_name="Betalningsinformation (Plain text)")
    payment_info_post_price_html = models.TextField(blank=True, verbose_name="Betalningsinformation efter pris (HTML)")
    payment_info_post_price_plain_text = models.TextField(blank=True, verbose_name="Betalningsinformation efter pris (Plain text)")

    class Meta:
        verbose_name = "Evenemangsinställningar"
        verbose_name_plural = verbose_name


class SiteSettings(SingeltonModel):
    show_warning_banner = models.BooleanField(default=False, verbose_name="Visa varningstext")
    warning_banner_text = models.TextField(blank=True, verbose_name="Varningstext")
    fadderiet_footer_left = models.TextField(blank=True, verbose_name="Footer vänster")
    fadderiet_footer_right = models.TextField(blank=True, verbose_name="Footer höger")

    fadderiet_logo = models.ImageField(null=True, blank=True, verbose_name="Fadderiets logga")
    fohseriet_logo = models.ImageField(null=True, blank=True, verbose_name="Föhseriets logga")

    class Meta:
        verbose_name = "Sidinställningar"
        verbose_name_plural = verbose_name
