import re
from collections import Iterable

from django.core.exceptions import ValidationError
from django.db import models


def validate_no_emoji(value):
    regex = re.compile(r'[^\u0000-\uFFFF]+')
    if regex.search(value):
        raise ValidationError("Tyvärr kunde innehållet inte göras om till en accepterad sträng (ex. inga emojis).")


class IntegerChoices(models.IntegerChoices):
    @classmethod
    def list_parse(cls, value):
        returning_list = []
        if isinstance(value, Iterable):
            for val in value:
                if isinstance(val, str):
                    matching_list = [cls(v) for v in cls.values if str(v) == val]
                    if len(matching_list) == 1:
                        returning_list.append(matching_list[0])
                    else:
                        raise ValueError("Value '%s' not found in Enum." % val)
                else:
                    raise TypeError("Parsing is only for string values.")
            else:
                return returning_list
        elif value is None:
            return returning_list

        raise TypeError("Wrong input target. Must be list of strings.")

    @classmethod
    def get_max_length(cls):
        return ",".join([str(v) for v in cls.values])
