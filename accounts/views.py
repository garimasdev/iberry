from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView
from accounts.models import User
from accounts.serializers import AccountSerializer
from dashboard.views import UserAccessMixin
from django.views.generic import ListView
from django.db.models import Q

# Create your views here.
class UsersViewPage(UserAccessMixin, ListView):
    permission_required = 'accounts.view_accounts'
    template_name = "tabs/user/users_list.html"
    serializer_class = AccountSerializer
    model = User
    queryset = User.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.all()
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data