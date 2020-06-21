from django.db import models
from django.core import exceptions
from django.forms.fields import TypedMultipleChoiceField


class MultipleStringChoiceField(models.CharField):
    def __init__(self, separator=",", **kwargs):
        self.separator = separator
        if not ('max_length' in kwargs):
            if not ("choices" in kwargs):
                raise KeyError("You must specify the choices option to MultipleStringChoiceField if you don't specify max_length.")

            max_length = len(self.separator.join([str(pair[0]) for pair in kwargs["choices"]]))
            kwargs['max_length'] = max_length

        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        return super().formfield(choices_form_class=TypedMultipleChoiceField)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        if self.separator != ",":
            kwargs['separator'] = self.separator
        return name, path, args, kwargs

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, list):
            return self.separator.join(value)

        if isinstance(value, str):
            return value

    def validate(self, value, model_instance):
        """
        Validate value and raise ValidationError if necessary. Subclasses
        should override this to provide validation logic.
        """

        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if self.choices is not None and value not in self.empty_values:
            for val in value.split(self.separator):
                for option_key, option_value in self.choices:
                    if isinstance(option_value, (list, tuple)):
                        # This is an optgroup, so look inside the group for
                        # options.
                        for optgroup_key, optgroup_value in option_value:
                            if val == optgroup_key:
                                return
                    elif val == option_key:
                        return
                raise exceptions.ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'], code='null')

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(self.error_messages['blank'], code='blank')
