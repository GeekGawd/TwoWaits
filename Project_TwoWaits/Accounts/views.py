# ------ rest framework imports -------
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
# ------ models --------
from .models import UserAccount

# ------ django AUTH ------
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password

from .serializers import (
    AccountSerializer
)


class NewAccount(APIView):
    permission_classes = (AllowAny,)
    
    # create a new account
    def post(self, request, format = None):
        serializer = AccountSerializer(data=request.data)
        user_email = request.data.get("email",)
        # checking if user already exists
        if UserAccount.objects.filter(email__iexact = user_email).exists():
            message = {'message':'User already exists. Please Log-In'}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

        else:
            # for validation of password (default and custom)
            # validate_password throws exception for valdation errors
            if request.data.get('password',)=='':
                return Response({'message':'Please enter a password'},status=status.HTTP_403_FORBIDDEN)

            try:
                validate_password(request.data.get('password',))
                if serializer.is_valid():
                    # send_otp(user_email)
                    serializer.save()
                return Response(serializer.data)
            except:
                message = 'Please Enter a valid password. Password should have atleast 1 Capital Letter, 1 Number and 1 Special Character in it. Also it should not contain 123'
                return Response({'message': message},status=status.HTTP_400_BAD_REQUEST)


class LoginAccount(APIView):
    permission_classes = (AllowAny,)

    serializer_class = AccountSerializer

    def post(self, request):
        email = (request.data.get("email",))
        password = request.data.get("password",)
        try:
            entered_usr = UserAccount.objects.get(email__iexact=email)
            if check_password(password,entered_usr.password ):
                if not entered_usr.is_verified:
                    message = {'message':'Email address not verified by otp. Please Verify.'}
                    # send_otp(email)
                    return Response(message, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    message = {'message':'Login verified'}
                    return Response(message, status=status.HTTP_202_ACCEPTED)
            else:
                message = {'message':'Incorrect password'}
                return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        except:
            message = {'message':'No matching user found'}
            return Response(message, status=status.HTTP_406_NOT_ACCEPTABLE)
        # check_pswd returns True for match
