from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(username)
        print(password)
        try:
            users = UserModel.objects.filter(Q(username__exact=username) | Q(email__exact=username))
            if not users:
               raise ValidationError("No account with this email.")
            for user in users:
                if username == user.username:
                    user = user
                elif username == user.email:
                    user = user
            print(users)
        except UserModel.DoesNotExist:
            raise ValidationError("No account with this email.")
        if user.check_password(password):
            return user
        else:
            raise ValidationError("The password does not match.")