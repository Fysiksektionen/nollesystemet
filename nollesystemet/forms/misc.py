import django.forms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Button, Submit


class ExtendedMetaModelForm(forms.ModelForm):
    """
    Allow the setting of any field attributes via the Meta class.
    """

    def __init__(self, *args, **kwargs):
        """
        Iterate over fields, set attributes from Meta.field_args.
        """
        super(ExtendedMetaModelForm, self).__init__(*args, **kwargs)
        if hasattr(self.Meta, "field_args"):
            # Look at the field_args Meta class attribute to get
            # any (additional) attributes we should set for a field.
            field_args = self.Meta.field_args
            # Iterate over all fields...
            for fname, field in self.fields.items():
                # Check if we have something for that field in field_args
                fargs = field_args.get(fname)
                if fargs:
                    # Iterate over all attributes for a field that we
                    # have specified in field_args
                    for attr_name, attr_val in fargs.items():
                        if attr_name.startswith("+"):
                            merge_attempt = True
                            attr_name = attr_name[1:]
                        else:
                            merge_attempt = False
                        orig_attr_val = getattr(field, attr_name, None)
                        if orig_attr_val and merge_attempt and \
                                type(orig_attr_val) == dict and \
                                type(attr_val) == dict:
                            # Merge dictionaries together
                            orig_attr_val.update(attr_val)
                        else:
                            # Replace existing attribute
                            setattr(field, attr_name, attr_val)


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


def make_crispy_form(form_class, submit_button=None, form_action=None):
    class CrispyForm(form_class):
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.add_input(Submit('submit', submit_button or 'Submit'))
            self.helper.form_action = form_action or ''
            super().__init__(*args, **kwargs)

    return CrispyForm
