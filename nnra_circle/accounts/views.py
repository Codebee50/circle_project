from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm, OtpForm, ResetPasswordForm
from django.contrib.auth.models import User
from .utils import generate_send_otp_code
from .models import Otpcode, Profile, Office
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .serializers import ProfileSerializer
from django.contrib.auth.decorators import login_required
from .utils import render_404, user_exists, validate_otp_code, render_error_page


# Create your views here.
def view_profile(request, uid):
    try:
        profile = Profile.objects.prefetch_related('office','user').get(user__id =uid)
    except Profile.DoesNotExist:
        profile = None

    return render(request, 'accounts/profile.html', {
            'profile': profile
        })

@login_required
def log_out(request):
    logout(request)
    return redirect('/')


def get_user_profile(request, profile_id):
    if request.method == 'POST':
        try: 
            # profile = Profile.objects.filter(id=profile_id).select_related('user', 'office')
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return JsonResponse({
                'status': 404,
                'message': 'Profile not found'
            }, status=404)
        
        serialiazer = ProfileSerializer(profile)

        return JsonResponse({
            'status': 200, 
            'message': 'Success',
            'profile': serialiazer.data
        }, status=200)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        try:
           profile = Profile.objects.prefetch_related('office').get(user=request.user)
           user = User.objects.get(id=request.user.id)
        except Profile.DoesNotExist:
           return JsonResponse({
               'message': 'Profile not found', 
               'status': 404,
               'data': {}
           }, status=404)
        except User.DoesNotExist:
            return JsonResponse({
               'message': 'user not found', 
               'status': 404,
               'data': {}
           }, status=404)
        
        firstname= request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        department = request.POST.get('department')
        username = request.POST.get('username')
        about = request.POST.get('about')
        phone = request.POST.get('phone')
        if firstname == '' or lastname == '':#ensure that user has provided a first ane last name
           return JsonResponse({
               'message': 'Firstname and Lastname cannot be left blank, please provide a value',
               'status': 400, 
               'data': {}
           }, status=400)

        if len(phone) >11:
            return JsonResponse({
               'message': 'Phone number cannot be greater than 11 digits',
               'status': 400, 
               'data': {}
           }, status=400)

        if user.first_name != firstname:
            user.first_name = firstname
        
        if user.last_name != lastname:
            user.last_name = lastname

        if profile.about != about:
            profile.about = about
        
        if profile.phone != phone:
            profile.phone = phone
        
        if user.username != username:
            user.username = username

        
        if profile.office.id != department:
            try:
                office = Office.objects.get(id=department)
            except Office.DoesNotExist:
                return JsonResponse({
                    'message': 'Invalid department',
                    'status': 400,
                    'data': {}
                }, status=400)
            
            profile.office = office

        user.save()
        profile.save()
        return JsonResponse({
           'message': 'Profile Updated successfully',
           'status': 200, 
           'data': {}
       }, status=200)
    
    elif request.method == 'GET':
        offices = Office.objects.all()
        user = request.user
        try:
            profile = Profile.objects.prefetch_related('user', 'office').get(user=user)
        except Profile.DoesNotExist:
            profile = None

        return render(request, 'accounts/editprofile.html', {
            'offices': offices,
            'profile': profile
        })

@login_required
def update_user_profile_photo(request, action):
    if request.method == 'POST':
        user= request.user
        try:
            user_profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return JsonResponse({
                'message': "Profile not found",
                'status': 404,
                'data': {}
            }, status=404)
            
        if action == 'remove':
            if user_profile.profileImg == 'def-user-img.png':
                return JsonResponse({
                    'message': 'Cannot remove default profile photo',
                    'status': 400,
                    'data': {}
                }, status=400)
            
            user_profile.profileImg.delete(save=False)
            user_profile.profileImg = 'def-user-img.png'
            user_profile.save()
            return JsonResponse({
                'message': 'Image removed successfully',
                'status': 200,
                'data': {}
            }, status=200)
        
        elif action == 'change':
            new_photo = request.FILES.get('new-photo')
            if new_photo:
                if user_profile.profileImg != 'def-user-img.png':
                    user_profile.profileImg.delete()
                
                user_profile.profileImg = new_photo
                user_profile.save()
                return JsonResponse({
                    'message': 'Photo updated successfully', 
                    'status': 200,
                    'data': {}
                }, status=200)
            else:
                return JsonResponse({
                    'message': 'Please choose a document',
                    'status': 400,
                    'data': {}
                }, status=400)
            
        else:
            return JsonResponse({
                'message': "Action not available, choices are 'remove' and 'change'",
                'status': 405,
                'data': {}
            }, status=405)
    
    else: 
        return JsonResponse({
            'message': 'Method not allowed',
            'status': 405,
            'data' : {}
        }, status=405)

def welcome_user(request, uid):
    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        return render_404(request)
    
    return render(request, 'registration/regcomplete.html', {
        'user': user
    })

def select_dept(request, uid):
    offices = Office.objects.all()

    if request.method == 'GET':
        return render(request,'registration/select-dept.html', {
            'offices': offices,
            'uid': uid})
    elif request.method == 'POST':
        office_name = request.POST.get('office_name')
        
        #get the selected office
        try: 
            office = Office.objects.get(office_name=office_name)
        except Office.DoesNotExist:
            office = None
            return JsonResponse({
                'status': 404, 
                'message': 'Office not found'
            }, status=404)

        #Get the user
        try: 
            user = User.objects.get(id=uid)
            profile = user.profile.first()
        except User.DoesNotExist:
            user= None
            return JsonResponse({
                'status': 404, 
                'message': 'User not found'
            }, status=404)
        
        if profile:
            profile.office = office
            profile.save()
            return JsonResponse({
                'status': 200, 
                'message': 'Department set successfully'
            }, status=200)
        else:
             return JsonResponse({
                'status': 404, 
                'message': 'User profile not found'
            }, status=404)

def resend_password_reset_code(request, uid):
    user = user_exists(uid)

    if user is not None:
        if generate_send_otp_code(user=user, type=Otpcode.Type.PASSWORD_RESET):
            messages.success(request, f"A new password reset code has been sent to {user.email}")
        else:
            messages.error(request, 'An error occured while resending your password reset code.')
    else:
        messages.error(request, 'FATAL: An error occured')
    
    return redirect('accounts:confirmreset', uid=user.id)
    
def resend_activation_code(request, uid):
    #get the user
    user = user_exists(uid)

    #generate and resend an activation code for that user
    if user is not None:
        user_profile = user.profile.first()
        if user_profile is not None and user_profile.is_email_verified:
            messages.success(request, 'Your email is already verified, please login to use your account.')
            return redirect('accounts:confirmcode', uid=user.id)
        
        code_sent = generate_send_otp_code(user=user, type=Otpcode.Type.AUTHENTICATION)
        if code_sent:
            messages.success(request, f"A new verification code has been sent to {user.email}.")
        else:
            messages.error(request, 'An error occured while resending your verification code.')
    else:
        messages.error(request, 'Fatal: An error occured.')
    
    return redirect('accounts:confirmcode', uid=user.id)

def reset_password(request, uid, code):
    user = user_exists(uid)
    if not user:
        return render_404(request)
    
    valid_code, reason = validate_otp_code(code, Otpcode.Type.PASSWORD_RESET, user)

    if not valid_code:
        return render_error_page(request, "The provided url is expired or invalid") 

    time_to_expiry = valid_code.get_tte()

    if request.method == 'GET':
        form = ResetPasswordForm()
    elif request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            password = cd['password']

            user.set_password(password)
            user.save()

            valid_code.used = True
            valid_code.save()
            messages.success(request, 'Password reset successful, you can now login using your newly created password.')
            return redirect('accounts:login')
    
    return render(request, 'registration/confirmresetcode.html', {
        'form': form,
        'user': user,
        'view': 'reset',
        'tte': time_to_expiry
    })

def confirm_reset_code(request, uid):
    try:
        user =User.objects.get(id=uid)
    except User.DoesNotExist:
        return render_404(request)

    if request.method == 'GET':
        form = OtpForm()
    elif request.method == 'POST':
        form = OtpForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            code = cd['code']

            otpcode, reason = validate_otp_code(code, Otpcode.Type.PASSWORD_RESET, user)
            if otpcode:
                # messages.success(request, reason)
                return redirect('accounts:passwordreset', uid=user.id, code=code)
            else:
                messages.error(request, reason)
                return render(request, 'registration/confirmresetcode.html', {
                        'form': form,
                        'user': user,
                        'view': 'confirm'
                    })
    return render(request, 'registration/confirmresetcode.html', {
        'form': form,
        'user': user,
        'view': 'confirm'
    })

def confirmcode(request, uid):
    #get the user with the uid
    try:
        user =User.objects.get(id=uid)
        profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        user= None
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'GET':
        form = OtpForm()
    elif request.method == 'POST':
        form = OtpForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            code= cd['code']
            otpcode = user.otpcode.filter(type= Otpcode.Type.AUTHENTICATION).first()

            #check if the users account is already verified
            if profile and profile.is_email_verified:  
                if profile.office:
                    messages.success(request, 'Your email is already verified, please login to use your account.')
                    return render(request, 'registration/confirmotp.html', {
                            'form': form,
                            'user': user
                    })
                else:
                    return redirect('accounts:selectdept', uid=user.id)

            #Validate otpcode
            if otpcode.code == code:
                #ensure otp code has not expired
                if otpcode.expired == True:
                    messages.error(request, "The code provided is expired, please reqeust a new one")
                    return render(request, 'registration/confirmotp.html', {
                            'form': form,
                            'user': user
                        })

                #Ensure otpcode has not been used
                if otpcode.used == True:
                    messages.error(request, "The code provided has been used, please request a new one")
                    return render(request, 'registration/confirmotp.html', {
                            'form': form,
                            'user': user
                        })
                
                otpcode.used = True
                otpcode.save()

                #create a user profile
                if not profile:
                    user_profile = Profile(user=user, is_email_verified=True)
                    user_profile.save()
                
                #activate the user
                user.is_active = True
                user.save()
                return redirect('accounts:selectdept', uid=user.id)
            else: 
                messages.error(request, 'Invalid code, please check the code in your mail and try again')
        else:
            messages.error('Invalid input')
        
    return render(request, 'registration/confirmotp.html', {
        'form': form,
        'user': user
    })

def reqeust_reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Email does not exist.')
            return render(request, 'registration/requestreset.html')
        
        code_sent = generate_send_otp_code(user, Otpcode.Type.PASSWORD_RESET)
        if code_sent:
            return redirect('accounts:confirmreset', uid=user.id)
        else:
            messages.error(request, 'An error occured')
    return render(request, 'registration/requestreset.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
    
            user = authenticate(request, username=cd['email'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    if Profile.objects.filter(user=user).exists():
                        messages.error(request, 'Your account seems to be deactivated at this moment, please seek admin support.')
                    else:
                        return redirect('accounts:resendcode', uid=user.id)
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'An error occured.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        register_form = UserRegistrationForm(request.POST)
    
        if register_form.is_valid():               
            cd = register_form.cleaned_data

            #create new user account
            user = register_form.save(commit=False)
            user.set_password(cd['password'])
            user.is_active = False
            user.save()

            code_sent = generate_send_otp_code(user=user, type=Otpcode.Type.AUTHENTICATION)
            if code_sent:
                return redirect('accounts:confirmcode', uid=user.id)
            else:
                messages.error(request, 'An error occured')
        else:
            messages.error(request, 'Kindly address the identified errors')
    else:
        register_form = UserRegistrationForm()

    return render(request, 'registration/register.html', {
        'form': register_form
    } )