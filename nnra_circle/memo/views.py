from django.shortcuts import render
from accounts.models import Office, Profile
from django.http import JsonResponse
import json
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Memo, MemoDocument, RecipientType, MemoRecipient
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from .utils import paginate
from accounts.utils import render_404
from django.views.decorators.http import require_POST

# Create your views here.
@require_POST
@login_required
def delete_memo(request, mid):
    try:
        memo = Memo.objects.get(id=mid)
    except Memo.DoesNotExist:
        return JsonResponse({
            'message': 'Memo not found',
            'status': 404,
            'data': {}
        }, status=404)
    
    memo.delete()
    return JsonResponse({
        'message': 'Memo deleted successfully',
        'status': 200,
        'data': {}
    })

@login_required
def memo_list(request):
    user = request.user
    try:
        profile = Profile.objects.select_related('office').get(user__id=user.id)
    except Profile.DoesNotExist:
        return JsonResponse({
            'message': 'Profile not found', 
            'status': 404, 
            'data': {}
        })
    
    lookup_one = Q(rec_type=RecipientType.DEPARTMENT) & Q(recipient_id=profile.office.id)
    lookup_two = Q(rec_type=RecipientType.INDIVIDUAL) & Q(recipient_id=user.id)
    lookup_three = Q(rec_type=RecipientType.ALL)
    recipient_list = MemoRecipient.objects.filter(lookup_one | lookup_two | lookup_three).select_related('memo')
    page_number= request.GET.get('page')

    recipients = paginate(recipient_list, 10, page_number)

    return render(request, 'memo/list.html', {
        'recipients': recipients,
        'user_profile': profile
    })

def memo_detail(request, mid):
    try:
        memo = Memo.objects.select_related('sender').get(id=mid) 
    except Memo.DoesNotExist:
        return render_404(request=request)


    supporting_documents = MemoDocument.objects.filter(memo=memo)

    return render(request, 'memo/detail.html', {
        'memo': memo,
        'documents': supporting_documents
    })


def distribute_memo(memo, recipient_list, user, request=None, documentcount=0):
    domain = get_current_site(request)    
    sender = 'Nigerian Nuclear Regulatory Authority <' + str(settings.EMAIL_HOST_USER) + '>' 
    email_body = render_to_string('emails/memo.html', {
        'sender': user,
        'memo': memo,
        'domain': domain,
        'documentcount': documentcount

    })
    text_content = strip_tags(email_body)

    email = EmailMultiAlternatives(
            memo.title,
            text_content,
            sender,
            recipient_list
        )
    
    email.attach_alternative(email_body, 'text/html')
    email.send()

def create_memo(title, body, image, rec_type, sender):
    if image:
        memo = Memo.objects.create(title=title, body=body, image=image, rec_type=rec_type, sender=sender)
    else:
        memo = Memo.objects.create(title=title, body=body, rec_type=rec_type, sender=sender)

    return memo

@login_required
def create(request):
    if request.method == 'GET':
        offices = Office.objects.all()
        profiles = Profile.objects.filter(user__is_active=True).select_related('user', 'office')
        return render(request, 'memo/create.html', {
            'offices': offices,
            'user_profiles': profiles,
        })
    

    elif request.method == 'POST':
        memo_title = request.POST.get('memo-title')
        memo_body = request.POST.get('memo-body')
        memo_image = request.FILES.get('memo-image')
        files= request.FILES.getlist('files')
        audience = request.POST.get('audience')

        sender_profile = Profile.objects.get(user=request.user)
        if audience == 'departments':
            memo = create_memo(title=memo_title, body=memo_body, image=memo_image, rec_type=RecipientType.DEPARTMENT, sender=sender_profile)
            selected_departments = json.loads(request.POST.get('selected-departments'))
            recipients_profile = Profile.objects.filter(office__id__in=selected_departments).select_related('user')
            for department in selected_departments:
                MemoRecipient.objects.create(memo=memo, rec_type=RecipientType.DEPARTMENT, recipient_id=department)
        
        if audience == 'individuals':
            memo = create_memo(title=memo_title, body=memo_body, image=memo_image, rec_type=RecipientType.INDIVIDUAL, sender=sender_profile)

            selected_individuals = json.loads(request.POST.get('selected-individuals'))
            recipients_profile = Profile.objects.filter(id__in=selected_individuals).select_related('user')
            for profile  in recipients_profile:
                MemoRecipient.objects.create(memo=memo, rec_type=RecipientType.INDIVIDUAL, recipient_id=profile.user.id)
        
        if audience == 'all':
            memo = create_memo(title=memo_title, body=memo_body, image=memo_image, rec_type=RecipientType.ALL, sender=sender_profile)
            recipients_profile = Profile.objects.all().select_related('user')
            MemoRecipient.objects.create(memo=memo, rec_type=RecipientType.ALL)

        documentcount = 0
        for file in files:
            documentcount += 1
            MemoDocument.objects.create(memo=memo, document=file, doc_name=file.name)

        recipients_emails = list(recipients_profile.values_list('user__email', flat=True))
        distribute_memo(memo, recipients_emails, request.user, request, documentcount)

        return JsonResponse({
            'message': 'Memo distributed successfully', 
            'status': 200,
            'data': {
                'url': memo.get_absolute_url(),
            }
        }, status=200)
    

def test(): 
    pass