from django import template
import datetime 
register = template.Library()


import datetime
from django import template

register = template.Library()

from datetime import date

from datetime import datetime, date

@register.filter
def get_item(dictionary, key):
    """
    A custom template filter to safely retrieve a value from a dictionary
    by key. Ensures that the key and dictionary keys are both datetime.date objects.
    """

    # Ensure the key is now a datetime.date object
    if isinstance(key, date):
        # print(dictionary, key)  # For debugging/
        if dictionary.get(key):
            print(dictionary, key) 
            return "green"
            
    return dictionary.get(key, None)

