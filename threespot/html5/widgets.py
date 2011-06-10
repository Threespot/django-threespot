from django.forms.widgets import Input

class EmailInput(Input):
    """
    An <input type="email"> HTML5 form type.
    """
    input_type = 'email'

class URLInput(Input):
    """
    An <input type="url"> HTML5 form type.
    """
    input_type = 'url'

class NumberInput(Input):
    """
    An <input type="number"> HTML5 form type.
    """
    input_type = 'number'

class RangeInput(Input):
    """
    An <input type="range"> HTML5 form type.
    """
    input_type = 'range'