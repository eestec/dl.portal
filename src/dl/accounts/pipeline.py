"""
Defines extra pipeline functions for the django-social-auth application
which make it play nice with the Account system of the Distance Learning
application.
"""

from accounts.models import Student


def create_member(*args, **kwargs):
    if kwargs['is_new']:
        user = kwargs['user']
        new_student = Student(name=user.first_name,
                              surname=user.last_name,
                              email=user.email)
        new_student.save(user=user)

def user_set_active(*args, **kwargs):
    """
    django-social-auth pipeline function which sets the user to active.
    All users authenticated by a social mechanism are exempt from email
    validation/activation.
    """
    if kwargs['is_new']:
        user = kwargs['user']
        if not user.is_active:
            user.is_active = True
            user.save()
