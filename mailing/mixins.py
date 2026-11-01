from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model

User = get_user_model()


def is_manager(user: User):
    if not user or not user.is_authenticated:
        return False

    if user.groups.filter(name='manager').exists():
        return True


class OwnerOrManagerMixin:

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if is_manager(user):
            return qs

        return qs.filter(owner=user)


class OwnerCheckMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        obj = self.get_object()

        if is_manager(user):
            return super().dispatch(request, *args, **kwargs)

        if hasattr(obj, 'owner') and obj.owner == user:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden("Вы не можете редактировать или удалять чужие данные.")