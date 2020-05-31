import nollesystemet.utils as utils
import utils.helper_views as helper_views


class FohserietMenuMixin(helper_views.MenuMixin):
    menu_item_info = utils.menu_item_info_fohseriet
    menu_items = ['index', 'hantera-event', 'hantera-andvandare', 'fadderiet', ['logga-in', 'logga-ut']]


class FadderietMenuMixin(helper_views.MenuMixin):
    menu_item_info = utils.menu_item_info_fadderiet
    menu_items = ['index', 'schema', 'bra-info', 'om-fadderiet', 'evenemang', 'kontakt', 'mina-sidor:profil', ['logga-in', 'logga-ut']]


class HappeningOptionsMixin:
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        return form

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        drink_option_formset = context['drink_option_formset']
        base_price_formset = context['base_price_formset']
        extra_option_formset = context['extra_option_formset']
        if drink_option_formset.is_valid() and base_price_formset.is_valid() and extra_option_formset.is_valid():
            print("in")
            response = super().form_valid(form)

            drink_option_formset.instance = self.object
            drink_option_formset.save()

            base_price_formset.instance = self.object
            base_price_formset.save()

            extra_option_formset.instance = self.object
            extra_option_formset.save()
            return response
        else:
            return super().form_invalid(form)