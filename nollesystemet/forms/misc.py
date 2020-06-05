import django.forms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Button, Submit
from django.forms import inlineformset_factory
from django.forms.formsets import DELETION_FIELD_NAME


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


def get_formset_form_helper(input_names, input_placeholders, wrapper_class=None, input_css_class=None,
                            formclass=None):
    helper = FormHelper()
    helper.layout = Layout(
        Row(
            *(Column(
                Field(name, placeholder=placeholder, wrapper_class=wrapper_class, css_class=css_class),
                css_class="col-5")
                for name, placeholder, css_class in zip(input_names, input_placeholders,
                                                        input_css_class if input_css_class else [''] * len(
                                                            input_names))),
            Column(Button(name="Ta bort", value="Ta bort", wrapper_class=wrapper_class,
                          css_class="btn-danger remove-" + formclass), css_class="col-2"),
        )
    )
    helper.form_tag = False
    return helper

def custom_inlineformset_factory(parent_model, object_model, model_fields, model_fields_placeholders, formclass, **kwargs):
    class FormClass(ExtendedMetaModelForm):
        class Meta:
            model = object_model
            fields = model_fields
            field_args = {filed_name: {'label': ''} for filed_name in model_fields}

        helper = get_formset_form_helper(model_fields,
                                         model_fields_placeholders,
                                         wrapper_class="pr-2 rb-1",
                                         formclass=formclass)

    kwargs['can_delete'] = True
    kwargs['form'] = FormClass
    formset_class = inlineformset_factory(parent_model, object_model, **kwargs)

    class FormsetClass(formset_class):
        def add_fields(self, form, index):
            super().add_fields(form, index)
            form.fields[DELETION_FIELD_NAME].widget = forms.widgets.HiddenInput(attrs={"type": "hidden", "value": ''})

    return FormsetClass


def make_crispy_form(form_class, submit_button=None, form_action=None):
    class CrispyForm(form_class):
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.add_input(Submit('submit', submit_button or 'Submit'))
            self.helper.form_action = form_action or ''
            super().__init__(*args, **kwargs)

    return CrispyForm


class CreateSeeUpdateModelForm(ExtendedMetaModelForm):
    def __init__(self, is_editable_args=(), editable=True, **kwargs):
        super(CreateSeeUpdateModelForm, self).__init__(**kwargs)

        self.is_new = self.instance.pk is None
        self.is_editable = self.get_is_editable(*is_editable_args, editable=editable, **kwargs) if editable is None else editable

        for field_name in self.fields:
            self.fields[field_name].disabled = not self.is_editable
            self.fields[field_name].widget.attrs['disabled'] = not self.is_editable

        self.helper = self.get_form_helper()

    def get_is_editable(self, *args, **kwargs):
        return self.is_new

    def get_form_helper(self, submit_name=None, form_tag=True):
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_tag = form_tag
        if self.is_editable and form_tag:
            helper.add_input(Submit('submit', submit_name if submit_name else ('Skicka' if self.is_new else 'Spara')))

        return helper




