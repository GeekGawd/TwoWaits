# ------ rest framework imports -------
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

# ------ models --------
from .models import UserAccount, OTP

from .serializers import (
    AccountSerializer,
)

# ------ django AUTH ------
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password

# -------utilities-------
from random import randint
from Project_TwoWaits.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from datetime import timedelta

# ------OTP-------
otp_expire_duration = 2


# -------CHANGE TO CLASS BASED--------
# ------ For Sending OTP to passed E-Mail -------
def send_otp(email):
    # generating 4-digit OTP
    otp = randint(1000,9999)
    # getting account
    user = UserAccount.objects.get(email=email)
    try:
        OTP.objects.create(otp_account_id=user, otp=otp)

    except:
        new_otp = OTP.objects.get(otp_account_id=user)
        new_otp.otp = otp
        new_otp.created = timezone.now()
        new_otp.save()
        
    from_email, to = EMAIL_HOST_USER, email
    subject = "OTP for TwoWaits Sign-Up"
    text_content = f'Your One Time Password for signing up on V-Shop is {otp}.\nValid for only 2 minutes.\nDO NOT SHARE IT WITH ANYBODY.'
    html_content = f'<span style="font-family: Arial, Helvetica, sans-serif; font-size: 16px;"><p style="font-size: 18px;">DO NOT SHARE IT WITH ANYBODY.</p><p>Valid for only {otp_expire_duration} minutes.</p><p>Your One Time Password for signing up on Two Waits is <strong style="font-size: 18px;">{otp}</strong>.</p></span>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
#------------------------------------------------

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


class OtpVerify(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            send_otp(request.data.get('email',))
            message = {'message':'OTP sent'}
            return Response(message, status=status.HTTP_200_OK)
        except:
            message = {'message':'OTP could not be sent'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        email = request.data.get("email",)
        entered_otp = request.data.get("otp",)
        # send_otp(email)
        try:
            user = UserAccount.objects.get(email__iexact = email)

            if str(user.otp) == str(entered_otp):
                expiry = user.otp.created + timedelta(minutes=otp_expire_duration)
                current = timezone.now()
                print(expiry)
                print(current)
                if expiry < current:
                    message = {'message':'OTP expired'}
                    return Response(message, status=status.HTTP_406_NOT_ACCEPTABLE)
                    
                else:
                    print("yessss")
                    user.is_verified = True
                    user.save()
                    message = {'message':'OTP matched account verified'}
                    return Response(message, status=status.HTTP_202_ACCEPTED)
            else:
                message = {'message':'OTP doesn\'t match'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
        except:
            message = {'message':'User not found'}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)


# Flow : Direct after OTP verification
class ForgotResetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email",) or request.user.email
        new_password = request.data.get("new_password")
        try:
            user = UserAccount.objects.get(email__iexact = email)
            print(user.password)
            print(new_password)

            if check_password(new_password, user.password):
                message = {'message':'Password cannot be same as old one'}
                return Response(message, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                try:
                    validate_password(new_password)
                except:
                    message = 'Please Enter a valid password. Password should have atleast 1 Capital Letter, 1 Number and 1 Special Character in it. Also it should not contain 123'
                    return Response({'message': message},status=status.HTTP_400_BAD_REQUEST)
                
                user.password = make_password(new_password)
                user.save()
                message = {'message':'Password Changed Successfully'}
                return Response(message, status=status.HTTP_202_ACCEPTED)
        except:
            message = {'message':'User not found'}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)