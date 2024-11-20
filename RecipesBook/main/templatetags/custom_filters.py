from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    return value.split(delimiter)



def startswith(value, arg):
    """
    Перевіряє, чи починається рядок value з аргументу arg.
    """
    if isinstance(value, str) and isinstance(arg, str):
        return value.startswith(arg)
    return False