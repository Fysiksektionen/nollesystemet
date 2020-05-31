from django.views.generic import TemplateView
import nollesystemet.mixins as mixins

class FadderietMenuView(mixins.FadderietMenuMixin, TemplateView):
    pass

class FohserietMenuView(mixins.FohserietMenuMixin, TemplateView):
    pass
