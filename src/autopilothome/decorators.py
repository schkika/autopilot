from functools import wraps
from django.http import HttpResponse


def only_administrators():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_full_access:
                return HttpResponse("Vi niste administrator i nemate \
                        ovlaštenje da pristupite ovoj strani !")
                #return redirect(view_to_return)
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def work_with_users():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_full_access and not request.user.can_add_user:
                return HttpResponse("Vi niste administrator i nemate \
                        ovlaštenje da pristupite ovoj strani !")
                #return redirect(view_to_return)
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def work_with_assosiates():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_full_access and not request.user.can_add_assosiate:
                return HttpResponse("Vi niste administrator i nemate \
                        ovlaštenje da pristupite ovoj strani !")
                #return redirect(view_to_return)
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def work_with_subjects():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_full_access and not request.user.can_open_subject:
                return HttpResponse("Vi niste administrator i nemate \
                        ovlaštenje da pristupite ovoj strani !")
                #return redirect(view_to_return)
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def work_with_clients():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_full_access and not request.user.can_add_client:
                return HttpResponse("Vi niste administrator i nemate \
                        ovlaštenje da pristupite ovoj strani !")
                #return redirect(view_to_return)
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator