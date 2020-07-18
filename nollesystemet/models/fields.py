from django.db import models
from django.core import exceptions
from django.forms.fields import TypedMultipleChoiceField, MultipleChoiceField


class SingleChoiceEnumModelField(models.CharField):
    def __init__(self, enum_class, **kwargs):
        self.enum_class = enum_class
        kwargs["choices"] = enum_class.choices
        kwargs['max_length'] = max([len(str(val)) for val in self.enum_class.values])
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        args.append(self.enum_class)
        return name, path, args, kwargs

class MultipleChoiceEnumModelField(models.CharField):
    def __init__(self, enum_class, separator=",", none_is_all=False, **kwargs):
        self.separator = separator
        self.enum_class = enum_class
        self.none_is_all = none_is_all
        kwargs["choices"] = enum_class.choices
        max_length = len(self.separator.join([str(pair[0]) for pair in kwargs["choices"]]))
        kwargs['max_length'] = max_length
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        return super().formfield(choices_form_class=TypedMultipleChoiceField)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.separator != ",":
            kwargs['separator'] = self.separator
        args.append(self.enum_class)
        return name, path, args, kwargs

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            if self.separator in value:
                return [self.parse_to_choice(val) for val in value.split(self.separator)]
            else:
                return self.parse_to_choice(value)
        if isinstance(value, list):
            if isinstance(value[0], str):
                return [self.parse_to_choice(val) for val in value]
            else:
                return value

    def clean(self, value, model_instance):
        super().clean(value, model_instance)
        if self.none_is_all:
            if value == "" or value is None:
                value = [self.enum_class.__getattr__(enum_entity.name) for enum_entity in self.enum_class]
        return value

    def get_prep_value(self, value):
        return self.separator.join([str(val.value) for val in value])

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def parse_to_choice(self, string_value):
        return [self.enum_class.__getattr__(enum_entity.name) for enum_entity in self.enum_class
                if str(enum_entity.value) == string_value][0]

    def validate(self, value, model_instance):
        """
        Validate value and raise ValidationError if necessary. Subclasses
        should override this to provide validation logic.
        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return
        if self.choices is not None and value not in self.empty_values:
            for val in value:
                for option in self.choices:
                    if isinstance(option, list):
                        # This is an optgroup, so look inside the group for
                        # options.
                        for optgroup in option:
                            if (val.value, val.label) == optgroup:
                                return
                    elif (val.value, val.label) == option:
                        return

                raise exceptions.ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': (val.value, val.label)},
                )

        if (value is None or None in value) and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'], code='null')

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(self.error_messages['blank'], code='blank')
