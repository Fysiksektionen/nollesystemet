import django.forms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Button, Submit, Div, HTML
from django.forms import inlineformset_factory, modelformset_factory
from django.forms.formsets import DELETION_FIELD_NAME


class ExtendedMetaModelForm(forms.ModelForm):
    """
    Allow the setting of any field attributes via the Meta class.

    Special case:
    Setting widget_class (and widget_attrs) sets Field.widget = widget_class(attrs=widget_attrs).
    This makes the field reload its widget on every forms instance. Important for forms rendered
    differently in different instances (eg. enabled/disabled).
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
                    if 'widget' not in fargs and 'widget_class' in fargs:
                        widget_attrs = fargs.get('widget_attrs', {})
                        setattr(field, 'widget', fargs['widget_class'](attrs=widget_attrs))

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
                            prefix="__prefix-placeholder__"):
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
                          css_class="btn-danger remove-" + prefix + "-form-btn"), css_class="col-2"),
        )
    )
    helper.form_tag = False
    return helper


def custom_inlineformset_factory(parent_model, object_model, model_fields, model_fields_placeholders, **kwargs):
    formset_class = inlineformset_factory(parent_model, object_model, fields='__all__')

    class FormClass(ExtendedMetaModelForm):
        class Meta:
            model = object_model
            fields = model_fields
            field_args = {filed_name: {'label': ''} for filed_name in model_fields}

        helper = get_formset_form_helper(model_fields,
                                         model_fields_placeholders,
                                         wrapper_class="pr-2 rb-1",
                                         prefix=formset_class.get_default_prefix())

    kwargs['can_delete'] = True
    kwargs['form'] = FormClass
    formset_class = inlineformset_factory(parent_model, object_model, **kwargs)

    class FormsetClass(formset_class):
        def add_fields(self, form, index):
            super().add_fields(form, index)
            form.fields[DELETION_FIELD_NAME].widget = forms.widgets.HiddenInput(attrs={"type": "hidden", "value": ''})

    return FormsetClass


def make_form_crispy(form_class, submit_button=None, form_action=None):
    class CrispyForm(form_class):
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.add_input(Submit('submit', submit_button or 'Submit'))
            self.helper.form_action = form_action or ''
            super().__init__(*args, **kwargs)

    return CrispyForm


class ModifiableModelForm(ExtendedMetaModelForm):
    def __init__(self,
                 editable=None, deletable=False,
                 submit_name=None, delete_name=None, form_tag=True,
                 exclude_fields=None, is_editable_args=None, is_deletable_args=None,
                 **kwargs):
        # Call to super for field init
        super(ModifiableModelForm, self).__init__(**kwargs)

        # Evaluate/save variables for deciding rendering-logic
        self.is_new = self.instance.pk is None
        self.is_editable = self.get_is_editable(*(is_editable_args or ())) if editable is None else editable
        self.is_deletable = self.get_is_deletable(*(is_deletable_args or ())) if deletable is None else deletable

        self.submit_name = submit_name
        self.delete_name = delete_name

        # Exclude dynamically unwanted fields (not rendered by Layout when not present)
        if exclude_fields is not None:
            for field_name in exclude_fields:
                if field_name in self.fields:
                    self.fields.pop(field_name)

        # Disable / enable if required.
        for field_name in self.fields:
            if not self.is_editable:
                self.fields[field_name].disabled = not self.is_editable
                self.fields[field_name].widget.attrs['disabled'] = str(not self.is_editable)
            if not self.is_editable or self.fields[field_name].disabled:
                self.fields[field_name].required = False

        # Get standard form helper with user Layout.
        self.helper = self.get_form_helper(form_tag)
        # Add Submit and Delete to form Layout
        self.append_submits()

    def get_is_editable(self, *args):
        """ Tells if form is deletable. Run *before* self.is_editable is set. """
        return self.is_new

    def get_is_deletable(self, *args):
        """ Tells if form is deletable. Run *after* self.is_editable is set. """
        return self.is_editable and not self.is_new

    def get_form_helper(self, form_tag=True):
        """ Returns the crispy forms form helper to be used. """
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_tag = form_tag
        helper.layout = Layout(
            *[Field(field_name) for field_name in self.fields]
        )
        return helper

    def append_submits(self):
        """ Appends the correct configuration of submit buttons to self.helper.layout. """
        if self.is_editable:
            if self.helper.form_tag:
                self.helper.layout.fields.append(
                    Row(
                        Column(HTML(self.submit_button), css_class="d-flex justify-content-start"),
                        Column(HTML(self.delete_button if self.is_deletable else ""),
                               css_class="d-flex justify-content-end")
                    )
                )

    @property
    def submit_button(self):
        """ Returns HTML representation of the submit button based of the settings given to the form. """
        val = self.submit_name if self.submit_name else ('Skicka' if self.is_new else 'Spara')
        return """<button type="submit" name="submit" class="btn btn-primary" id="submit-id-submit">
                   """ + val + """ <i class="fa fa-save" aria-hidden="true"></i>
               </button>"""

    @property
    def delete_button(self):
        """ Returns HTML representation of the delete button based of the settings given to the form. """
        if not self.is_new:  # New object can not have delete-button
            val = self.delete_name if self.delete_name else 'Radera'
            return """<button type="submit" name="delete" class="btn btn-danger" id="submit-id-delete">
                       """ + val + """ <i class="fa fa-trash" aria-hidden="true"></i>
                   </button>"""
        else:
            return ""

    @property
    def submit_delete_buttons(self):
        """ Returns HTML representation of the select and delete buttons based of the settings given to the form. """
        if not self.is_new:
            return """<div class="d-flex flex-row">
                         <div class="d-flex justify-content-start col p-0">
                             """ + self.submit_button + """
                         </div>
                         <div class="d-flex justify-content-end col p-0">
                             """ + self.delete_button + """
                         </div>
                    </div>"""
        else:
            return """<div class="d-flex flex-row justify-content-start">
                         <div class="d-flex justify-content-start col p-0">
                             """ + self.submit_button + """
                         </div>
                    </div>"""

    def delete_instance(self):
        """
        Deletes the current instance form database and from form.
        This sets instance=None and resets form.
        """
        if self.instance.pk is not None:
            self.instance.delete()
        self.__init__(instance=None)


class MultipleModelsModifiableForm(ModifiableModelForm):
    extra_form_classes = None

    def __init__(self, **kwargs):
        # Initialize the main form
        super().__init__(**kwargs)
        # Initialize extra forms
        self.extra_forms = []
        self.num_of_extras = 0
        self.field_to_form_dict = {field_name: -1 for field_name in self.fields}
        if self.extra_form_classes is not None:
            self.num_of_extras = len(self.extra_form_classes)
            self.extra_instances = self.get_extra_instances()
            self.extra_initial = self.get_extra_initial()

            if len(self.extra_instances) != self.num_of_extras:
                raise Exception("Lists of extra_instances does not match number of extra forms."
                                "Make sure they are of the same length.")
            if len(self.extra_initial) != self.num_of_extras:
                raise Exception("Lists of extra_initial does not match number of extra forms."
                                "Make sure they are of the same length.")

            self.extra_forms = self.get_extra_forms(kwargs_list=([kwargs] * self.num_of_extras))
            # Add fields form forms to main form.
            for i, form in enumerate(self.extra_forms):
                for field_name, field in form.fields.items():
                    if field_name not in self.fields:
                        self.fields[field_name] = field
                        self.field_to_form_dict[field_name] = i
                    else:
                        raise Exception("The field " +
                                        field_name +
                                        "appeared in multiple forms of the same MultipleModelsModifiableForm. "
                                        "This is not allowed")

        self.helper = self.late_get_form_helper(form_tag=kwargs.get('form_tag', None))
        self.append_submits()

    def late_get_form_helper(self, form_tag=True):
        return self.get_form_helper()

    def get_extra_instances(self):
        return [None] * self.num_of_extras

    def get_extra_initial(self):
        return [None] * self.num_of_extras

    def _post_clean(self):
        for i, form in enumerate(self.extra_forms):
            form.full_clean()
            for field_name, error in form.errors.items():
                self.add_error(field_name, error)

        super()._post_clean()

    def get_extra_forms(self, kwargs_list=None):
        extra_forms = []
        if kwargs_list is None:
            kwargs_list = [{}] * len(self.extra_form_classes)
        for i, form_class in enumerate(self.extra_form_classes):
            kwargs = kwargs_list[i].copy()
            kwargs.update({
                'instance': self.extra_instances[i],
                'initial': self.extra_initial[i],
                'data': self.data,
                'files': self.files,
            })
            extra_forms.append(form_class(**kwargs))
        return extra_forms

    def get_initial_for_field(self, field, field_name):
        i = self.field_to_form_dict[field_name]
        if i >= 0:
            return self.extra_forms[i].get_initial_for_field(field, field_name)
        else:
            return super(ModifiableModelForm, self).get_initial_for_field(field, field_name)

    def save(self, commit=True):
        if self.extra_forms is not None:
            if len([True for form in self.extra_forms if form.errors]) == 0:
                for form in self.extra_forms:
                    form.save(commit=commit)
        return super().save(commit)

    def delete_instance(self):
        for form in self.extra_forms:
            form.delete_instance()
        super().delete_instance()
