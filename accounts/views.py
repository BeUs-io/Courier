from django.contrib.auth.views import (
    PasswordChangeView as DjangoPasswordChangeView
)
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render, get_object_or_404
from core.utils.utils import redirect_to_another_url
from django.utils.decorators import method_decorator
from django.views import generic
from accounts import forms, models, email
from django.contrib import messages
from django.urls import reverse_lazy
from core.utils.decorator import CHANGE, VIEW, DELETE, ADD, perms_require
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from accounts.decorators import login_required


class LoginView(auth_views.LoginView):
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if user.is_staff or user.is_superuser:
            return HttpResponseRedirect(self.get_success_url())
        return redirect('assetdash')


@method_decorator([login_required(False)], name="dispatch")
class AccountTemplateView(generic.TemplateView):
    template_name = "accounts/accounts.html"
    extra_context = {'title': "Account"}


@method_decorator([login_required(False)], name="dispatch")
class AccountProfileView(generic.FormView):
    template_name = "accounts/profile_form.html"
    extra_context = {}
    form_class = forms.AccountProfileModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.request.user.get_full_name()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('account_profile')
        context = self.get_context_data(kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


@method_decorator([login_required(False)], name="dispatch")
class AccountDeleteView(generic.FormView):
    template_name = "accounts/account_delete_form.html"
    extra_context = {}
    form_class = forms.AccountDeleteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Delete Account"
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            request.user.delete()
            messages.success(request, "Account delete successfully!")
            return redirect('auth_login')
        context = self.get_context_data(kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


@method_decorator([login_required(False)], name="dispatch")
class PasswordChangeView(DjangoPasswordChangeView):
    template_name = "accounts/account_password_change.html"
    form_class = forms.PasswordChangeForm
    success_url = reverse_lazy('auth_password_change_done')

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        if True:
            update_session_auth_hash(self.request, form.user)
            messages.success(self.request, "Password successfully changed!")
            self.success_url = reverse_lazy('assetdash')
        return super().form_valid(form)


@method_decorator([login_required(staff=True), perms_require(f"auth.{VIEW}group")], name="dispatch")  # noqa
class UserGroupListView(generic.ListView):
    template_name = "accounts/groups_list.html"
    extra_context = {
        'segment': 'user', 'sub_segment': "user_groups", "title": "Group"
    }
    queryset = models.Group.objects.prefetch_related("permissions").all()


@method_decorator([login_required(staff=True), perms_require(f"auth.{ADD}group")], name="dispatch")  # noqa
class UserGroupCreateView(generic.FormView):
    template_name = "accounts/groups_form.html"
    extra_context = {
        'segment': 'user', 'sub_segment': "user_groups", "title": "New Group"
    }
    form_class = forms.UserGroupModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form_obj = form.save()
            models.UserLogs.create_log(
                request, form_obj, models.ADDITION, changed_data=None
            )
            messages.success(request, f"{form_obj.name} add successfully!")
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True)], name="dispatch")
class UserGroupUpdateView(generic.FormView):
    template_name = "accounts/groups_form.html"
    extra_context = {'segment': 'user', 'sub_segment': "user_groups"}

    @method_decorator([perms_require(f"auth.{VIEW}group")])
    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(models.Group, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['instance'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context

    @method_decorator([perms_require(f"auth.{CHANGE}group")])
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form_obj = form.save()
            models.UserLogs.create_log(
                request, form_obj, models.CHANGE,
                changed_data=form.changed_data
            )
            messages.success(request, f"{form_obj.name} updated successfully!")
            return redirect(redirect_to_another_url(request, form_obj))
        context = self.get_context_data(kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


@method_decorator([login_required(staff=True), perms_require(f"auth.{DELETE}group")], name="dispatch")  # noqa
class UserGroupDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            group_obj = get_object_or_404(models.Group, pk=kwargs['pk'])
            name = group_obj.name
            models.UserLogs.create_log(
                request, group_obj, models.DELETION, changed_data=None
            )
            group_obj.delete()
            messages.success(request, f"{name.title()} delete successfully!")
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('user_groups_list')


@method_decorator([login_required(staff=True), perms_require(f"accounts.{VIEW}users")], name="dispatch")  # noqa
class UserListView(generic.TemplateView):
    template_name = "accounts/user_list.html"
    extra_context = {'segment': 'user', 'sub_segment': "user", "title": "User"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = models.Users.objects.all()
        return context


@method_decorator([login_required(staff=True), perms_require(f"accounts.{ADD}users")], name="dispatch")  # noqa
class UserCreateView(generic.FormView):
    template_name = "accounts/user_form.html"
    extra_context = {
        'segment': 'user', 'sub_segment': "user", "title": "New User"
    }
    form_class = forms.UserModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form_obj = form.save()
            models.UserLogs.create_log(
                request, form_obj, models.ADDITION, changed_data=None
            )
            if form.cleaned_data['password']:
                form_obj.set_password(form.cleaned_data['password'])
                form_obj = form.save()
            messages.success(request, f"{form_obj.email} add successfully!")
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True)], name="dispatch")
class UserUpdateView(generic.FormView):
    template_name = "accounts/user_form.html"
    extra_context = {'segment': 'user', 'sub_segment': "user"}
    form_class = forms.UserModelForm

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(models.Users, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['instance'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.email
        return context

    @method_decorator([perms_require(f"accounts.{VIEW}users")])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator([perms_require(f"accounts.{CHANGE}users")])
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.fields.pop('password')
        form.fields.pop('password2')
        if form.is_valid():
            form_obj = form.save()
            models.UserLogs.create_log(
                request, form_obj, models.CHANGE,
                changed_data=form.changed_data
            )
            messages.success(request, f"{form_obj.name} updated successfully!")
            return redirect(redirect_to_another_url(request, form_obj))
        context = self.get_context_data(kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


@method_decorator([login_required(staff=True), perms_require(f"accounts.{DELETE}users")], name="dispatch")  # noqa
class UserDeleteView(generic.View):

    def get(self, request, *args, **kwargs):
        try:
            user_obj = get_object_or_404(models.Users, pk=kwargs['pk'])
            email = user_obj.email
            models.UserLogs.create_log(
                request, user_obj, models.DELETION, changed_data=None
            )
            user_obj.delete()
            messages.success(request, f"{email} delete successfully!")
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('user_list')


@method_decorator([login_required(staff=True), perms_require(f"accounts.{ADD}users")], name="dispatch")  # noqa
class UserInviteView(generic.FormView):
    template_name = "accounts/user_invite_form.html"
    extra_context = {
        'segment': 'user', 'sub_segment': "user", 'title': "Invite User"
    }
    form_class = forms.UserInviteModelForm
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        form_obj = form.save()
        models.UserLogs.create_log(
            self.request, form_obj, models.ADDITION, changed_data=None
        )
        token, _ = models.UserToken.make_token(
            form_obj,
            models.UserToken.TokenType.INVITE
        )
        context = {
            "url": reverse_lazy('set_password', kwargs={'token': token})
        }
        email.UserInviteEmail(self.request, context).send([
            form_obj.email
        ])
        messages.success(
            self.request,
            f"{form.cleaned_data['email']} invite successfully!"
        )
        return super().form_valid(form)


class UserInviteSetPassword(generic.FormView):
    template_name = "accounts/set_password.html"
    form_class = forms.UserInviteSetPassword
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        self.object = models.UserToken.check_token(
            token=self.kwargs['token'],
            type=models.UserToken.TokenType.INVITE
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object.user.set_password(form.cleaned_data['password'])
        self.object.user.is_active = True
        self.object.user.save()
        messages.success(self.request, f"{self.object.user.email} password set successfully!")  # noqa
        self.object.delete()
        self.request.session.flush()
        return redirect('user_invite_complete')


class UserInviteComplete(generic.TemplateView):
    template_name = "accounts/invite_complete.html"


@method_decorator([login_required(staff=True), perms_require(f"accounts.{CHANGE}users")], name="dispatch")  # noqa
class UserPasswordUpdateView(generic.FormView):
    template_name = "accounts/password_update.html"
    extra_context = {'segment': 'user', 'sub_segment': "user"}
    form_class = forms.UserPasswordUpdateForm

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(models.Users, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {'email': self.object.email}
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object.set_password(form.cleaned_data['password'])
            messages.success(request, f"{self.object.email} password updated successfully!")  # noqa
            return redirect(redirect_to_another_url(request, self.object))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True), perms_require(f"accounts.{VIEW}designationmodel")], name="dispatch")  # noqa
class DesignationListView(generic.TemplateView):
    template_name = "accounts/designation_list.html"
    extra_context = {
        'segment': 'user', 'sub_segment': "designation",
        "title": "Designation"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = models.DesignationModel.objects.all()
        return context


@method_decorator([login_required(staff=True), perms_require(f"accounts.{ADD}designationmodel")], name="dispatch")  # noqa
class DesignationCreateView(generic.FormView):
    template_name = "accounts/designation_form.html"
    extra_context = {
        'segment': 'user', 'sub_segment': "designation",
        "title": "New Designation"
    }
    form_class = forms.DesignationModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form_obj = form.save()
            models.UserLogs.create_log(
                request, form_obj, models.ADDITION, changed_data=None
            )
            messages.success(request, f"{form_obj.title} add successfully!")
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True)], name="dispatch")
class DesignationUpdateView(generic.FormView):
    template_name = "accounts/designation_form.html"
    extra_context = {'segment': 'user', 'sub_segment': "designation"}
    form_class = forms.DesignationModelForm

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            models.DesignationModel, pk=kwargs['pk']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['instance'] = self.object
        return kwargs

    @method_decorator([perms_require(f"accounts.{VIEW}designationmodel")])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator([perms_require(f"accounts.{CHANGE}designationmodel")])
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form_obj = form.save()
            models.UserLogs.create_log(
                request, form_obj, models.CHANGE,
                changed_data=form.changed_data
            )
            messages.success(
                request, f"{self.object.title} updated successfully!"
            )
            return redirect(redirect_to_another_url(request, form_obj))
        context = self.get_context_data(kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


@method_decorator([login_required(staff=True), perms_require(f"accounts.{DELETE}designationmodel")], name="dispatch")  # noqa
class DesignationDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        designation_obj = get_object_or_404(
            models.DesignationModel, pk=kwargs['pk']
        )
        title = designation_obj.title
        models.UserLogs.create_log(
            request, designation_obj, models.DELETION, changed_data=None
        )
        designation_obj.delete()
        messages.success(request, f"{title} delete successfully!")
        return redirect('designation_list')


@method_decorator([login_required(staff=True)], name="dispatch")  # noqa
class UserLogsListView(generic.ListView):
    extra_context = {
        'segment': 'settings', 'sub_segment': "userlogs",
        "title": "User logs"
    }
    queryset = models.UserLogs.objects.select_related(
        "content_type", "user"
    )
    template_name = "accounts/user_logs_list.html"


class LogoutView(auth_views.LogoutView):

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)
