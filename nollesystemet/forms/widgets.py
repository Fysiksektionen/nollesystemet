from django.forms.widgets import FileInput, DateTimeInput


class ButtonFileWidget(FileInput):
    template_name = "fohseriet/elements/button-file-field.html"
    button_classes = "btn-primary col-12 col-md-8 col-lg-6 my-3"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        if 'class' in attrs:
            attrs['class'] = attrs['class'] + " autosubmit"
        else:
            attrs['class'] = "autosubmit"

        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['button_classes'] = self.button_classes
        print(context)
        return context

class BootstrapDateTimePickerInput(DateTimeInput):
    template_name = 'common/elements/datetime-widget.html'

    def get_context(self, name, value, attrs):
        datetimepicker_id = 'datetimepicker_{name}'.format(name=name)
        if attrs is None:
            attrs = dict()
        attrs['data-target'] = '#{id}'.format(id=datetimepicker_id)
        attrs['class'] = 'form-control datetimepicker-input'
        context = super().get_context(name, value, attrs)
        context['widget']['datetimepicker_id'] = datetimepicker_id
        return context