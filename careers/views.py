import time

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core import antispam
from careers.forms import ApplicationForm
from careers.models import JobPosting


def job_list(request):
    return render(request, "careers/list.html", {"jobs": JobPosting.objects.filter(is_active=True)})


def job_detail(request, pk):
    job = get_object_or_404(JobPosting, pk=pk, is_active=True)
    return _apply(request, job)


def general_application(request):
    return _apply(request, None)


def _apply(request, job):
    form = ApplicationForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if request.POST.get("website"):  # honeypot filled: silently drop
            return redirect(request.path)
        if time.time() - request.session.get("last_apply", 0) < 30:
            messages.error(request, "لطفاً چند ثانیه بعد دوباره تلاش کنید.")
        elif form.is_valid():
            err = antispam.check_submission(request, "apply", form.cleaned_data["message"], form.cleaned_data["field_of_study"],
                                            limit=3)
            if err:
                messages.error(request, err)
            else:
                app = form.save(commit=False)
                app.posting = job
                app.ip = antispam.client_ip(request)[:45]
                app.save()
                request.session["last_apply"] = time.time()
                messages.success(request, "رزومه شما با موفقیت ارسال شد. از همکاری شما سپاسگزاریم.")
                return redirect(request.path)
    return render(request, "careers/detail.html", {"job": job, "form": form, "challenge": antispam.new_challenge()})
