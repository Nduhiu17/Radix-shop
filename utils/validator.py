import re

from app.models import User


class Validate:
    '''Class for validating data input'''

    @staticmethod
    def validate_username_format(username):
        '''method to validate a username'''
        regex = r"^[1-9]\d*(\.\d+)?$"
        if re.match(regex, username):
            return True
        return False

    @staticmethod
    def validate_length_username(username):
        '''checking the username length no be not less than 6 characters'''
        if len(username) < 4:
            return False
        return True

    @staticmethod
    def validate_password_length(password):
        '''checking password length to be not less than 5 characters'''
        if len(password) < 6:
            return False
        return True

    @staticmethod
    def validate_email_format(email):
        '''checks correct email format'''
        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if re.match(regex, email, re.IGNORECASE):
            return True
        return False

    @staticmethod
    def is_admin(user_id):
        user = User.get_by_id(id=user_id)
        print(user)