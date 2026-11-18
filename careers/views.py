import time

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

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
        if time.time() - request.session.get("last_apply", 0) < 30:
            messages.error(request, "لطفاً چند ثانیه بعد دوباره تلاش کنید.")
        elif form.is_valid():
            app = form.save(commit=False)
            app.posting = job
            app.save()
            request.session["last_apply"] = time.time()
            messages.success(request, "رزومه شما با موفقیت ارسال شد. از همکاری شما سپاسگزاریم.")
            return redirect(request.path)
        elif "website" in form.errors:
            return redirect(request.path)
    return render(request, "careers/detail.html", {"job": job, "form": form})
