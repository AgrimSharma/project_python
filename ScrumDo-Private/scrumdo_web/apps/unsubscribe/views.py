from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from apps.brake.decorators import ratelimit
from rollbardecorator import catchlogexception
from .models import UnsubscribeRequest
from .tasks import unsubscribeEmailAddress


@ratelimit(rate='100/h', block=True, method=['POST'])
def unsubscribe_home(request):
    email = request.GET.get("email", "")
    if request.method == "POST":
        if request.POST.get("email", "") != "":
            _unsubscribe(request)
            return redirect("unsubscribe_confirm")

    return render_to_response('unsubscribe/unsubscribe_home.html',
                              {'email': email},
                              context_instance=RequestContext(request))



def unsubscribe_robot(request):
    email = request.GET.get("email", None)
    if email is not None:
        req = UnsubscribeRequest(email=email, ip=request.META["REMOTE_ADDR"], reason='Auto-Robot Unsubscribe')
        req.save()
        unsubscribeEmailAddress(email, 'Auto-Robot Unsubscribe')
    return render_to_response('unsubscribe/unsubscribe_confirm.html',
                              {'email': email},
                              context_instance=RequestContext(request))


@catchlogexception
def _createUnsubscribeRecord(request, reason):
    req = UnsubscribeRequest(email=request.POST.get("email",""), ip=request.META["REMOTE_ADDR"], reason=reason)
    req.save()


def _unsubscribe(request):
    if request.POST.get("reason") == "Other":
        reason = request.POST.get("reasonOther")
    else:
        reason = request.POST.get("reason")
    _createUnsubscribeRecord(request, reason)
    unsubscribeEmailAddress(request.POST.get("email"), reason)


def unsubscribe_confirm(request):
    email = request.POST.get("email")
    return render_to_response('unsubscribe/unsubscribe_confirm.html',
                              {'email': email},
                              context_instance=RequestContext(request))
