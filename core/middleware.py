from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """Users created with a bootstrap password must change it before using the dashboard."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and request.path.startswith("/admin/"):
            allowed = {reverse("admin:password_change"), reverse("admin:logout"), reverse("admin:password_change_done")}
            if request.path not in allowed and self._must_change(user):
                return redirect("admin:password_change")
        return self.get_response(request)

    @staticmethod
    def _must_change(user):
        initial = getattr(user, "initial_password", None)
        return initial is not None and initial.password_hash == user.password
