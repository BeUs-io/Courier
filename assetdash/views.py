from django.views import generic
from accounts.decorators import login_required
from django.utils.decorators import method_decorator
from dashboard import models
from assetdash import forms
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages


@method_decorator([login_required(False)], name='dispatch')
class AssetDashboard(generic.TemplateView):
    template_name = "assetdash/index.html"
    extra_context = {
        "title": "Asset Dashboard", "dashboard": True,
        'segment': 'assetdash'
    }


@method_decorator([login_required(False)], name='dispatch')
class AssetListView(generic.TemplateView):
    template_name = "assetdash/asset_list.html"
    extra_context = {
        "title": "Asset List", 'segment': 'asset'
    }


@method_decorator([login_required(False)], name='dispatch')
class AssetRequestListView(generic.ListView):
    template_name = "assetdash/asset_request_list.html"
    extra_context = {
        "title": "Asset Request List", 'segment': 'assetrequest'
    }

    def get_queryset(self):
        return models.AssetRequest.objects.filter(
            requested=self.request.user
        )


@method_decorator([login_required(False)], name='dispatch')
class AssetRequestCreateView(generic.CreateView):
    template_name = "assetdash/asset_request_form.html"
    extra_context = {
        "title": "Create Asset Request", 'segment': 'assetrequest'
    }
    form_class = forms.AssetRequestModelForm
    success_url = reverse_lazy("assetdash_request_list")

    def form_valid(self, form):
        form_obj = form.save(commit=False)
        form_obj.requested = self.request.user
        form_obj.request_date = timezone.now()
        form_obj.save()
        messages.success(self.request, "Asset Request created successfully")
        return super().form_valid(form)


@method_decorator([login_required(False)], name='dispatch')
class AssetRequestUpdateView(generic.UpdateView):
    template_name = "assetdash/asset_request_form.html"
    extra_context = {
        "title": "Update Asset Request", 'segment': 'assetrequest'
    }
    model = models.AssetRequest
    form_class = forms.AssetRequestModelForm
    success_url = reverse_lazy("assetdash_request_list")

    def form_valid(self, form):
        messages.success(self.request, "Asset Request updated successfully")
        return super().form_valid(form)


class AssetIssueListView(generic.ListView):
    template_name = "assetdash/asset_issue_list.html"
    extra_context = {
        "title": "Asset Issue List", 'segment': 'assetissue'
    }

    def get_queryset(self):
        return models.AssetIssue.objects.filter(
            raised_by=self.request.user
        )
