from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Button


def get_formset_form_helper(input_names, input_placeholders, wrapper_class=None, input_css_class=None, remove_button_css_class=None):
    helper = FormHelper()
    helper.layout = Layout(
        Row(
            *(Column(
                Field(name, placeholder=placeholder, wrapper_class=wrapper_class, css_class=css_class), css_class="col-5")
              for name, placeholder, css_class in zip(input_names, input_placeholders,
                                                      input_css_class if input_css_class else [''] * len(
                                                          input_names))),
            Column(Button(name="Ta bort", value="Ta bort", wrapper_class=wrapper_class,
                          css_class="btn-danger " + remove_button_css_class), css_class="col-2")
        )
    )
    helper.form_tag = False
    return helper
