from rest_framework.authentication import BaseAuthentication # Class to inherit that has pre-defined validations
from rest_framework.exceptions import AuthenticationFailed, NotFound # throws an exception
from rest_framework.response import Response
from django.contrib.auth import get_user_model # method that returns the current auth model
from django.conf import settings # import settings so we can get secret key
import jwt # import jwt so we can decode the token in the auth header

User = get_user_model() # saving auth model to a variable

# DOCUMENTATION FOR CUSTOM AUTH CLASSES:
# Explainer: https://www.django-rest-framework.org/api-guide/authentication/#how-authentication-is-determined
# Custom authentication class: https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication
class JWTAuthentication(BaseAuthentication):

    # This will act as the middleware that authenticates our secure routes
    def authenticate(self, request):
        # Make sure the access_token exists in the cookies, saving it to variable if it does
        access_token = request.COOKIES.get('access_token')

        # Check if header has a value, if it doesn't return None - None is returned when we want to invalidate the request
        if not access_token:
            raise AuthenticationFailed('Missing access token')

        # Get payload, take the sub (the user id) and make sure that user exists
        try:
            # 1st arg is the token itself
            # 2nd arg is the secret
            # 3rd argument is kwarg that takes the algorithm used
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])

            # find user
            user = User.objects.get(pk=payload.get('user_id'))

        # if jwt.decode errors, this except will catch it
        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationFailed(detail='Invalid Token')

        # If no user is found in the db matching the sub, the below will catch it
        except User.DoesNotExist:
            raise AuthenticationFailed(detail='User Not Found')

        # If all good, return the user and the token
        return (user, access_token)
    

    def authenticate_header(self, request):
        return 'Bearer'