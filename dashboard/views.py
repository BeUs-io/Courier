import pytz
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from core.utils.decorator import VIEW, ADD, CHANGE, DELETE, perms_require
from dashboard import forms, models
from django.contrib import messages
from django.utils.decorators import method_decorator
from core.utils.utils import redirect_to_another_url
from django.contrib.messages.views import SuccessMessageMixin
from accounts import models as ac_models
from accounts.decorators import login_required
from django.db.models import Count, F
from django.http import JsonResponse
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone


@method_decorator([login_required(staff=True)], name="dispatch")
class IndexTemplateView(generic.TemplateView):
    template_name = 'dashboard/index.html'
    extra_context = {
        "segment": "dashboard", "title": "Dashboard", "dashboard": True
    }

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff and request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('assetdash')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_count'] = ac_models.get_user_model().objects.count()
        context['designation_count'] = ac_models.DesignationModel.objects.count()  # noqa
        context['group_count'] = ac_models.Group.objects.count()
        context['asset_count'] = models.AssetModel.objects.count()
        context['asset_status_count'] = models.AssetStatusModel.objects.count()
        context['category_count'] = models.CategoryModel.objects.count()
        context['supplier_count'] = models.SupplierModel.objects.count()
        context['department_count'] = models.DepartmentModel.objects.count()
        return context


@method_decorator([login_required(staff=True)], name="dispatch")
class AssetRequestBarChartView(generic.View):
    def get(self, request, *args, **kwargs):
        start, end = request.GET.get('date').split('&')
        start_date = parse_date(start)
        end_date = parse_date(end)
        if start_date == end_date:
            end_date = start_date + timezone.timedelta(days=1)
        object_count = models.AssetRequest.objects.filter(
            created_at__range=(start_date, end_date)
        ).values(date=F('created_at')).annotate(count=Count('id'))
        object_count = [
            {
                'date': parse_datetime(str(obj['date'])).replace(
                    tzinfo=pytz.UTC
                ).astimezone(timezone.get_current_timezone()),
                'count': obj['count']
            } for obj in object_count
        ]
        return JsonResponse({'data': list(object_count)}, safe=False)


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}departmentmodel")], name="dispatch")  # noqa
class DepartmentListView(generic.ListView):
    extra_context = {
        'segment': 'user', 'sub_segment': "department", "title": "Department"
    }
    model = models.DepartmentModel
    template_name = "dashboard/department_list.html"


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{ADD}departmentmodel")], name="dispatch")  # noqa
class DepartmentCreateView(generic.CreateView):
    model = models.DepartmentModel
    form_class = forms.DepartmentModelForm
    template_name = 'dashboard/department_form.html'
    extra_context = {
        'segment': 'user', 'sub_segment': "department",
        "title": "New Department"
    }

    def form_valid(self, form):
        form_obj = form.save()
        messages.success(
            self.request,
            f"{form_obj.title} was created successfully"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.ADDITION, changed_data=None
        )
        return redirect(redirect_to_another_url(self.request, form_obj))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}departmentmodel")], name="dispatch")  # noqa
class DepartmentUpdateView(generic.UpdateView):
    extra_context = {'segment': 'user', 'sub_segment': "department"}
    model = models.DepartmentModel
    form_class = forms.DepartmentModelForm
    template_name = 'dashboard/department_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        self.extra_context['title'] = self.object.title
        return kwargs

    @method_decorator([perms_require(f"dashboard.{CHANGE}departmentmodel")])
    def form_valid(self, form):
        form_obj = form.save()
        messages.success(
            self.request, f"{form_obj.title} was updated successfully"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.ADDITION,
            changed_data=form.changed_data
        )
        return redirect(redirect_to_another_url(self.request, form_obj))


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{DELETE}departmentmodel")], name="dispatch")  # noqa
class DepartmentDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            department_obj = get_object_or_404(
                models.DepartmentModel, pk=kwargs['pk']
            )
            ac_models.UserLogs.create_log(
                self.request, department_obj, ac_models.DELETION,
                changed_data=None
            )
            title = department_obj.title
            department_obj.delete()
            messages.success(request, f"{title} delete successfully!")
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('department_list')


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}assetmodel")], name="dispatch")  # noqa
class AssetListView(generic.ListView):
    template_name = 'dashboard/asset_list.html'
    extra_context = {
        "segment": "asset", "sub_segment": "asset_list", "title": "Asset List"
    }
    queryset = models.AssetModel.objects.prefetch_related(
        'category', 'department'
    ).select_related('added_by', 'supplier', 'asset_status').all()


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{ADD}assetmodel")], name="dispatch")  # noqa
class AssetCreateView(generic.TemplateView):
    template_name = 'dashboard/asset_form.html'
    extra_context = {"segment": "asset", "sub_segment": "asset_list"}

    def get(self, request, *args, **kwargs):
        self.extra_context['title'] = "New Asset"
        asset_id = models.AssetModel.get_asset_id()
        self.extra_context['form'] = forms.AssetModelForm(
            initial={"asset_id": asset_id}, user=request.user
        )
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = forms.AssetModelForm(
            data=request.POST, files=request.FILES, user=request.user
        )
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.added_by = request.user
            form_obj.save()
            ac_models.UserLogs.create_log(
                self.request, form_obj, ac_models.ADDITION, changed_data=None
            )
            messages.success(request, f"{form_obj.title} add successfully!")
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True)], name="dispatch")
class AssetUpdateView(generic.TemplateView):
    template_name = 'dashboard/asset_form.html'
    extra_context = {"segment": "asset", "sub_segment": "asset_list"}

    @method_decorator([perms_require(f"dashboard.{VIEW}assetmodel")])
    def get(self, request, *args, **kwargs):
        asset_obj = get_object_or_404(models.AssetModel, pk=kwargs['pk'])
        self.extra_context['title'] = f"{asset_obj.asset_id}"
        self.extra_context['form'] = forms.AssetModelForm(
            instance=asset_obj, user=request.user
        )
        return super().get(request, *args, **kwargs)

    @method_decorator([perms_require(f"dashboard.{CHANGE}assetmodel")])
    def post(self, request, *args, **kwargs):
        asset_obj = get_object_or_404(models.AssetModel, pk=kwargs['pk'])
        form = forms.AssetModelForm(
            instance=asset_obj, data=request.POST, files=request.FILES,
            user=request.user
        )
        if form.is_valid():
            form_obj = form.save()
            messages.success(
                request, f"{form_obj.title} updated successfully!"
            )
            ac_models.UserLogs.create_log(
                self.request, form_obj, ac_models.CHANGE,
                changed_data=form.changed_data
            )
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{DELETE}assetmodel")], name="dispatch")  # noqa
class AssetDeleteView(generic.View):
    extra_context = {}

    def get(self, request, *args, **kwargs):
        try:
            asset_obj = get_object_or_404(models.AssetModel, pk=kwargs['pk'])
            title = asset_obj.title
            ac_models.UserLogs.create_log(
                self.request, asset_obj, ac_models.DELETION, changed_data=None
            )
            asset_obj.delete()
            messages.success(request, f"{title} delete successfully!")
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('asset_list')


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}assetstatusmodel")], name="dispatch")  # noqa
class AssetStatusListView(generic.TemplateView):
    template_name = 'dashboard/asset_status_list.html'
    extra_context = {
        "segment": "asset", "sub_segment": "asset_status",
        "title": "Asset Status"
    }

    def get(self, request, *args, **kwargs):
        self.extra_context['object_list'] = models.AssetStatusModel.objects.all()   # noqa
        return super().get(request, *args, **kwargs)


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{ADD}assetstatusmodel")], name="dispatch")  # noqa
class AssetStatusCreateView(generic.TemplateView):
    template_name = "dashboard/asset_status_form.html"
    extra_context = {
        "segment": "asset", "sub_segment": "asset_status",
        "title": "New Asset Status"
    }

    def get(self, request, *args, **kwargs):
        self.extra_context['form'] = forms.AssetStatusModelForm(user=request.user)  # noqa
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = forms.AssetStatusModelForm(data=request.POST, user=request.user)
        if form.is_valid():
            form_obj = form.save()
            messages.success(request, f"{form_obj.title} add successfully!")
            ac_models.UserLogs.create_log(
                self.request, form_obj, ac_models.ADDITION, changed_data=None
            )
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True)], name="dispatch")
class AssetStatusUpdateView(generic.TemplateView):
    template_name = "dashboard/asset_status_form.html"
    extra_context = {"segment": "asset", "sub_segment": "asset_status"}

    @method_decorator([perms_require(f"dashboard.{VIEW}assetstatusmodel")])
    def get(self, request, *args, **kwargs):
        asset_status_obj = get_object_or_404(
            models.AssetStatusModel, pk=kwargs['pk']
        )
        self.extra_context["title"] = asset_status_obj.title
        self.extra_context['form'] = forms.AssetStatusModelForm(
            instance=asset_status_obj, user=request.user
        )
        return super().get(request, *args, **kwargs)

    @method_decorator([perms_require(f"dashboard.{CHANGE}assetstatusmodel")])
    def post(self, request, *args, **kwargs):
        asset_status_obj = get_object_or_404(
            models.AssetStatusModel, pk=kwargs['pk']
        )
        form = forms.AssetStatusModelForm(
            data=request.POST, instance=asset_status_obj, user=request.user
        )
        if form.is_valid():
            form_obj = form.save()
            ac_models.UserLogs.create_log(
                self.request, form_obj, ac_models.CHANGE,
                changed_data=form.changed_data
            )
            messages.success(
                request, f"{form_obj.title} updated successfully!"
            )
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{DELETE}assetstatusmodel")], name="dispatch")  # noqa
class AssetStatusDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            asset_s_obj = get_object_or_404(
                models.AssetStatusModel, pk=kwargs['pk']
            )
            ac_models.UserLogs.create_log(
                self.request, asset_s_obj,
                ac_models.DELETION, changed_data=None
            )
            title = asset_s_obj.title
            asset_s_obj.delete()
            messages.success(request, f"{title} delete successfully!")
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('asset_status_list')


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}categorymodel")], name="dispatch")  # noqa
class CategoryListView(generic.TemplateView):
    template_name = "dashboard/category_list.html"
    extra_context = {
        "segment": "asset", "sub_segment": "category_list",
        "title": "Categories"
    }

    def get(self, request, *args, **kwargs):
        self.extra_context['object_list'] = models.CategoryModel.objects.all()
        return super().get(request, *args, **kwargs)


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{ADD}categorymodel")], name="dispatch")  # noqa
class CategoryCreateView(generic.TemplateView):
    template_name = "dashboard/category_form.html"
    extra_context = {
        "segment": "asset", "sub_segment": "category_list",
        "title": "New Category"
    }

    def get(self, request, *args, **kwargs):
        self.extra_context['form'] = forms.CategoryModelForm(user=request.user)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = forms.CategoryModelForm(data=request.POST, user=request.user)
        if form.is_valid():
            form_obj = form.save()
            messages.success(request, f"{form_obj.title} add successfully!")
            ac_models.UserLogs.create_log(
                self.request, form_obj, ac_models.ADDITION, changed_data=None
            )
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True)], name="dispatch")
class CategoryUpdateView(generic.TemplateView):
    template_name = "dashboard/category_form.html"
    extra_context = {"segment": "asset", "sub_segment": "category_list"}

    @method_decorator([perms_require(f"dashboard.{VIEW}categorymodel")])
    def get(self, request, *args, **kwargs):
        category_obj = get_object_or_404(models.CategoryModel, pk=kwargs['pk'])
        self.extra_context['title'] = category_obj.title
        self.extra_context['form'] = forms.CategoryModelForm(
            instance=category_obj, user=request.user
        )
        return super().get(request, *args, **kwargs)

    @method_decorator([perms_require(f"dashboard.{CHANGE}categorymodel")])
    def post(self, request, *args, **kwargs):
        category_obj = get_object_or_404(models.CategoryModel, pk=kwargs['pk'])
        form = forms.CategoryModelForm(
            instance=category_obj, data=request.POST, user=request.user
        )
        if form.is_valid():
            form_obj = form.save()
            messages.success(
                request, f"{form_obj.title} updated successfully!"
            )
            ac_models.UserLogs.create_log(
                self.request, form_obj, ac_models.CHANGE,
                changed_data=form.changed_data
            )
            return redirect(redirect_to_another_url(request, form_obj))
        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{DELETE}categorymodel")], name="dispatch")  # noqa
class CategoryDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            category_obj = get_object_or_404(
                models.CategoryModel, pk=kwargs['pk']
            )
            ac_models.UserLogs.create_log(
                self.request, category_obj, ac_models.DELETION,
                changed_data=None
            )
            title = category_obj.title
            category_obj.delete()
            messages.success(request, f"{title} delete successfully!")
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('category_list')


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}suppliermodel")], name="dispatch")  # noqa
class SupplierListView(generic.ListView):
    model = models.SupplierModel
    template_name = 'dashboard/supplier_list.html'
    extra_context = {"segment": "supplier", "title": "Supplier"}


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{ADD}suppliermodel")], name="dispatch")  # noqa
class SupplierCreateView(generic.CreateView):
    model = models.SupplierModel
    form_class = forms.SupplierModelForm
    template_name = 'dashboard/supplier_form.html'
    extra_context = {"segment": "supplier", "title": "Add Supplier"}

    def form_valid(self, form):
        form_obj = form.save()
        messages.success(
            self.request,
            f"{form_obj.title} was created successfully"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.ADDITION,
            changed_data=None
        )
        return redirect(redirect_to_another_url(self.request, form_obj))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}suppliermodel")], name="dispatch")  # noqa
class SupplierUpdateView(generic.UpdateView, SuccessMessageMixin):
    extra_context = {"segment": "supplier", "title": "Supplier"}
    model = models.SupplierModel
    form_class = forms.SupplierModelForm
    template_name = 'dashboard/supplier_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        self.extra_context['title'] = self.object.title
        return kwargs

    @method_decorator([perms_require(f"dashboard.{CHANGE}suppliermodel")])
    def form_valid(self, form):
        form_obj = form.save()
        messages.success(
            self.request, f"{form_obj.title} was updated successfully"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.CHANGE,
            changed_data=form.changed_data
        )
        return redirect(redirect_to_another_url(self.request, form_obj))


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{DELETE}suppliermodel")], name="dispatch")  # noqa
class SupplierDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            supplier_obj = get_object_or_404(
                models.SupplierModel, pk=kwargs['pk']
            )
            ac_models.UserLogs.create_log(
                self.request, supplier_obj, ac_models.DELETION,
                changed_data=None
            )
            title = supplier_obj.title
            supplier_obj.delete()
            messages.success(request, f"{title} delete successfully!")
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('supplier_list')


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}sssetrequest")], name="dispatch")  # noqa
class AssetRequestListView(generic.ListView):
    template_name = 'dashboard/asset_request_list.html'
    extra_context = {
        "segment": "asset", "sub_segment": "asset_request_list",
        "title": "Asset Request"
    }
    queryset = models.AssetRequest.objects.select_related(
        'asset', 'requested', 'approved_by'
    ).all()


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}sssetrequest")], name="dispatch")  # noqa
class AssetRequestUpdateView(generic.UpdateView, SuccessMessageMixin):
    extra_context = {"segment": "asset", "sub_segment": "asset_request_list"}
    queryset = models.AssetRequest.objects.select_related(
        'asset', 'requested', 'approved_by'
    ).all()
    form_class = forms.AssetRequestModelForm
    template_name = 'dashboard/asset_request_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        self.extra_context['title'] = self.object
        return kwargs

    @method_decorator([perms_require(f"dashboard.{CHANGE}sssetrequest")])
    def form_valid(self, form):
        form_obj = form.save(commit=False)
        form_obj.approved_by = self.request.user
        form_obj.save()
        messages.success(
            self.request, f"{form_obj.__str__()} was updated successfully"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.CHANGE,
            changed_data=form.changed_data
        )
        return redirect(redirect_to_another_url(self.request, form_obj))


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{DELETE}sssetrequest")], name="dispatch")  # noqa
class AssetRequestDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            asset_request_obj = get_object_or_404(
                models.AssetRequest, pk=kwargs['pk']
            )
            ac_models.UserLogs.create_log(
                self.request, asset_request_obj, ac_models.DELETION,
                changed_data=None
            )
            title = asset_request_obj
            asset_request_obj.delete()
            messages.success(
                request,
                f"{title.__str__()} delete successfully!"
            )
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('asset_request_list')


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}sssetissue")], name="dispatch")  # noqa
class AssetIssueListView(generic.ListView):
    queryset = models.AssetIssue.objects.select_related(
        'asset', 'status', 'raised_by'
    ).all()
    template_name = 'dashboard/asset_issue_list.html'
    extra_context = {
        "segment": "asset", "sub_segment": "asset_issue_list",
        "title": "Asset Issue"
    }


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{ADD}sssetissue")], name="dispatch")  # noqa
class AssetIssueCreateView(generic.CreateView):
    model = models.AssetIssue
    form_class = forms.AssetIssueModeForm
    template_name = 'dashboard/asset_issue_form.html'
    extra_context = {
        "segment": "asset", "sub_segment": "asset_issue_list",
        "title": "New Asset Issue"
    }

    def form_valid(self, form):
        form_obj = form.save()
        messages.success(
            self.request,
            f"{form_obj.__str__()} was created successfully"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.ADDITION,
            changed_data=None
        )
        return redirect(redirect_to_another_url(self.request, form_obj))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{VIEW}sssetissue")], name="dispatch")  # noqa
class AssetIssueUpdateView(generic.UpdateView, SuccessMessageMixin):
    extra_context = {"segment": "asset", "sub_segment": "asset_issue_list"}
    model = models.AssetIssue
    form_class = forms.AssetIssueModeForm
    template_name = 'dashboard/asset_issue_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        self.extra_context['title'] = self.object
        return kwargs

    @method_decorator([perms_require(f"dashboard.{CHANGE}sssetissue")])
    def form_valid(self, form):
        form_obj = form.save()
        messages.success(
            self.request,
            f"{form_obj.__str__()} was updated successfully"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.CHANGE,
            changed_data=form.changed_data
        )
        return redirect(redirect_to_another_url(self.request, form_obj))


@method_decorator([login_required(staff=True), perms_require(f"dashboard.{DELETE}sssetissue")], name="dispatch")  # noqa
class AssetIssueDeleteView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            asset_issue_obj = get_object_or_404(
                models.AssetIssue, pk=kwargs['pk']
            )
            ac_models.UserLogs.create_log(
                self.request, asset_issue_obj, ac_models.DELETION,
                changed_data=None
            )
            title = asset_issue_obj
            asset_issue_obj.delete()
            messages.success(
                request,
                f"{title.__str__()} delete successfully!"
            )
        except Exception as e:
            messages.error(request, f"Internal server error: {e}")
        return redirect('asset_issue_list')
