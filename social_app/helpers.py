import re

def is_valid_email(email):
    """
    Validates an email address using a regular expression.

    :param email: The email address to validate.
    :return: True if the email is valid, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    # Match the email against the regex pattern
    if re.match(email_regex, email):
        return True
    else:
        return False