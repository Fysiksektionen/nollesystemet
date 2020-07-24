import csv
from io import StringIO

import django.forms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Button, Submit, Div, HTML

from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, modelformset_factory
from django.forms.formsets import DELETION_FIELD_NAME
from django.templatetags.static import static


from .widgets import *

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

        self.add_fields(**kwargs)

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

    def add_fields(self, **kwargs):
        pass

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


class ObjectsAdministrationForm(forms.Form):
    model = None
    verbose_name_singular = None
    verbose_name_plural = None

    can_create = None
    can_delete = None
    can_upload = None
    can_download = None

    form_tag = None

    create_object_url = "#"
    download_url = "#"

    file_type = None
    upload_objects_file = forms.FileField(label='',
                                          required=False,
                                          allow_empty_file=False)
    upload_objects_file_data = None
    upload_js_file = "fohseriet/js/script-upload_objects_file.js"

    def __init__(self, can_create=None, can_delete=None, can_upload=None, can_download=None, **kwargs):
        super().__init__(**kwargs)

        # Load permissions
        self.can_create = self.can_create if self.can_create is not None else can_create or False
        self.can_delete = self.can_delete if self.can_delete is not None else can_delete or False
        self.can_upload = self.can_upload if self.can_upload is not None else can_upload or False
        self.can_download = self.can_download if self.can_download is not None else can_download or False

        # Set model related stuff
        if self.model is None:
            if 'model' not in kwargs:
                raise NotImplementedError("Please specify the model of the administration form.")
            else:
                self.model = kwargs['model']
        self.verbose_name_singular = self.verbose_name_singular or self.model.verbose_name
        self.verbose_name_plural = self.verbose_name_plural or self.model.verbose_name
        self.fields['upload_objects_file'].label = "Ladda upp %s" % self.verbose_name_plural

        # Allow subclasses to add fields dynamically
        self.add_fields(**kwargs)

        # Get crispy form helper
        self.form_tag = self.form_tag if self.form_tag is not None else kwargs.get('form_tag', True)
        self.helper = self.get_form_helper(self.form_tag)

        if self.file_type:
            if isinstance(self.file_type, str):
                self.file_type = self.file_type.lower()
            elif isinstance(self.file_type, list):
                self.file_type = [file_type.lower() for file_type in self.file_type]
            else:
                raise TypeError("file_type must be either a string or a list of strings.")

    def add_fields(self, **kwargs):
        """ Method for child classes to add extra fields to the form. Passed the kwargs of __init__. """
        pass

    def get_form_helper(self, form_tag=True):
        """ Returns the crispy forms form helper to be used. """
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_tag = form_tag

        button_classes = "btn col mb-4"

        helper.layout = Layout(
            Row(
                Column(
                    HTML(
                        """
                        <a class="%s" href="%s">
                        %s
                        <i class="fa fa-plus" aria-hidden="true"></i>
                        </a>
                        """ %
                        (button_classes + " btn-primary", self.create_object_url,
                         "Skapa ny %s" % self.verbose_name_singular.lower())
                    ),
                ),
                Column()
            ),
            Row(
                Column(
                    HTML(
                        """
                        <a class="%s" href="%s" type="submit" download>
                            %s
                            <i class="fa fa-download" aria-hidden="true"></i>
                        </a>
                        """ %
                        (button_classes + " btn-success", self.download_url,
                         "Ladda ned %s" % self.verbose_name_plural.lower())
                    ),
                ),
                Column(
                    HTML(
                        """
                        <button class="%s" name="delete" type="submit">
                            %s
                            <i class="fa fa-trash" aria-hidden="true"></i>
                        </button>
                        """ %
                        (button_classes + " btn-danger", "Radera alla %s" % self.verbose_name_plural.lower())
                    ),
                )
            ),
            Row(
                Column(
                    'upload_objects_file',
                    HTML(
                        """
                        <script type="text/javascript" id="script-upload_objects_file" src="%s"></script>
                        """ % (static(self.upload_js_file))
                    ),
                    css_class='col-12'
                ),
            ),
        )
        return helper

    def delete_all(self):
        self.model.objects.all().delete()

    def clean_upload_objects_file(self):
        """ Cleans and verifies uploaded file. """
        self.upload_objects_file_data = None
        if self.cleaned_data['upload_objects_file']:
            if self.file_type:
                ending = self.cleaned_data['upload_objects_file'].name.split('.')[1]
                if isinstance(self.file_type, str):
                    if ending.lower() != self.file_type.lower():
                        raise ValidationError("Fel filtyp. Accepterad filtyp är '%s'. Du laddade upp en fil av typ '%s'." %
                                              (self.file_type, ending))
                elif isinstance(self.file_type, list):
                    if ending not in [file_type.lower() for file_type in self.file_type]:
                        raise ValidationError("Fel filtyp. Accepterade filtyper är '%s'."
                                              "Du laddade upp en fil av typ '%s'." % (','.join(self.file_type), ending))

            self.upload_objects_file_data = self.read_and_verify_file_content()

    def read_and_verify_file_content(self):
        """
        Method to read the file into memory in the desired form.
        Override this in child classes for custom read and validation. Raise ValidationError on bad file content.
        :return file content as a python object for later use.
        """

        file = self.files.get('upload_objects_file')
        if file:
            return file.read()
        else:
            return None

class CsvFileAdministrationForm(ObjectsAdministrationForm):
    """
    Administration form with csv file upload. Subclass and fill the validation and parsing arrays.

    All columns in 'file_columns' must exist in either 'required_columns',
    'val_or_none_columns' or 'val_or_blank_str_columns'.

    Use 'enum_columns' and 'object_columns' to parse values at read.

    File data is saved as a list of the rows parsed as dicts with file_columns as keys.
    """

    file_type = 'csv'
    delimiter = ';'

    file_columns = None  # [column_name, ...]

    # Value exists validators
    required_columns = None  # [column_name, ...]
    val_or_none_columns = None  # [column_name, ...]
    val_or_blank_str_columns = None  # [column_name, ...]

    #
    enum_columns = None  # [(column_name, Enum class, is_nullable), ...]
    object_columns = None  # [(column_name, model, is_nullable), ...]

    def __init__(self, can_create=None, can_delete=None, can_upload=None, can_download=None, **kwargs):
        super().__init__(can_create=can_create, can_delete=can_delete, can_upload=can_upload, can_download=can_download,
                         **kwargs)

        self.validation_arrays = [self.required_columns, self.val_or_none_columns, self.val_or_blank_str_columns]
        self.parsing_arrays = [self.enum_columns, self.object_columns]
        for column_name in self.file_columns:
            in_arrays = [array for array in self.validation_arrays if column_name in array]
            if len(in_arrays) > 1:
                raise Exception("%s is defined in multiple validation column arrays. Exactly one allowed." % column_name)
            elif len(in_arrays) == 0:
                raise Exception("%s is not defined in any validation column arrays. Exactly one allowed." % column_name)

        for column_name in self.file_columns:
            in_arrays = [array for array in self.parsing_arrays if column_name in [tup[0] for tup in array]]
            if len(in_arrays) > 1:
                raise Exception("%s is defined in multiple parsing column arrays. Maximum one allowed." % column_name)

    def read_and_verify_file_content(self):
        file = self.files.get('upload_objects_file')
        if file:
            try:
                file = file.read().decode('utf-8')
                user_reader = csv.DictReader(StringIO(file), delimiter=self.delimiter, fieldnames=self.file_columns)
                next(user_reader)
            except:
                raise ValidationError("Filen kunde inte läsas.\n"
                                      "Se till att den har utf-8 format och %s som avskiljare." % self.delimiter)

            errors = []
            users = []
            for row, user_info in enumerate(user_reader):
                for column_name in self.file_columns:
                    if not user_info[column_name]:
                        if column_name in self.required_columns:
                            errors.append("%s saknas (på rad %d)." % (column_name, row + 1))
                        elif column_name in self.val_or_none_columns:
                            user_info[column_name] = None
                        elif column_name in self.val_or_blank_str_columns:
                            user_info[column_name] = ""

                for column_name, enum_class, is_nullable in self.enum_columns:
                    try:
                        user_info[column_name] = enum_class.__getattr__(user_info[column_name])
                    except AttributeError:
                        if is_nullable:
                            user_info[column_name] = None
                        else:
                            errors.append("%s kan inte göras till %s (på rad %d)." %
                                          (user_info[column_name], enum_class.__name__(), row + 1))

                for column_name, model, is_nullable in self.object_columns:
                    try:
                        user_info[column_name] = model.objects.get(name=user_info[column_name])
                    except model.DoesNotExist:
                        if is_nullable:
                            user_info[column_name] = None
                        else:
                            errors.append("%s kan inte göras till %s (på rad %d)." %
                                          (user_info[column_name], model.__name__(), row + 1))

                users.append(user_info)

            if errors:
                raise ValidationError("\n".join(errors))
            else:
                return users
        else:
            raise ValidationError("Filen hittades inte.")
