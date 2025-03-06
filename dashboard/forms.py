from django import forms
from dashboard import models
from crispy_forms import layout, helper
from core.utils.utils import get_form_button

textarea = forms.CharField(
    widget=forms.Textarea(attrs={'rows': 1}), required=False
)


class AssetModelForm(forms.ModelForm):
    description = textarea

    class Meta:
        model = models.AssetModel
        fields = (
            'asset_id', 'title', 'model', 'description', 'price',
            'asset_status', 'category', 'supplier', 'department',
            'image', 'is_active', 'receipt'
        )
        widgets = {
            'category': forms.SelectMultiple(
                attrs={'class': 'multiSelect2', 'multiple': 'multiple'}
            ),
            'department': forms.SelectMultiple(
                attrs={'class': 'multiSelect2', 'multiple': 'multiple'}
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.user = user
        self.fields['category'].queryset = models.CategoryModel.objects.filter(is_active=True)  # noqa
        self.fields['department'].queryset = models.DepartmentModel.objects.filter(is_active=True)  # noqa
        self.fields['asset_status'].queryset = models.AssetStatusModel.objects.filter(is_active=True, request=False)  # noqa
        button_title = "Save"
        delete = ""
        if self.instance.title:
            delete = self.instance
            self.fields['asset_id'].widget.attrs['readonly'] = True
            button_title = "Update"
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column('asset_id', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column(layout.HTML("""<svg id="barcode"></svg>""", ),
                              css_class='form-group col-md-6 d-flex justify-content-center mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('title', css_class='form-group col-md-6 mb-0'),
                layout.Column('model', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('description', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('category', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('price', css_class='form-group col-md-6 mb-0'),
                layout.Column('asset_status', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('supplier', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('department', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('image', css_class='form-group col-md-6 mb-0'),
                layout.Column('receipt', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'is_active',
            get_form_button(
                button_title, delete, user=self.user, model="assetmodel",
                app="dashboard"
            )
        )


class AssetStatusModelForm(forms.ModelForm):

    class Meta:
        model = models.AssetStatusModel
        fields = ('title', 'color', 'is_active', 'request')
        widgets = {
            'color': forms.TextInput(attrs={"type": "color"})
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.helper = helper.FormHelper()
        button_title = "Save"
        delete = ""
        if self.instance.title:
            delete = self.instance
            button_title = "Update"
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column('title', css_class='form-group col-md-6 mb-0'),
                layout.Column('color', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('is_active', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('request', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            get_form_button(
                button_title, delete, user=self.user, model="assetstatusmodel",
                app="dashboard"
            )
        )


class DepartmentModelForm(forms.ModelForm):
    model_name = "departmentmodel"
    app_name = "dashboard"

    class Meta:
        model = models.DepartmentModel
        fields = ('title', 'description', 'is_active')
        widgets = {'description': forms.Textarea(attrs={'rows': 1})}

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.helper = helper.FormHelper()
        button_title = "Save"
        delete = ""
        if self.instance.title:
            button_title = "Update"
            delete = self.instance

        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column('title', css_class='form-group col-md-6 mb-0'),
                layout.Column('description', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            'is_active',
            get_form_button(
                button_title, delete, user=self.user, model=self.model_name,
                app=self.app_name
            )
        )


class CategoryModelForm(DepartmentModelForm):
    model_name = "categorymodel"
    app_name = "dashboard"

    class Meta:
        model = models.CategoryModel
        fields = ('title', 'description', 'is_active')
        widgets = {'description': forms.Textarea(attrs={'rows': 1})}


class SupplierModelForm(forms.ModelForm):
    class Meta:
        model = models.SupplierModel
        fields = ('title', 'email', 'phone', 'address', 'extra', 'is_active')
        widgets = {"extra": forms.Textarea(attrs={'rows': 1})}

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        button_title = "Save"
        delete = ""
        if self.instance.title:
            button_title = "Update"
            delete = self.instance
        self.helper.layout = layout.Layout(
            "title",
            layout.Row(
                layout.Column('email', css_class='form-group col-md-6 mb-0'),
                layout.Column('phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('address', css_class='form-group col-md-6 mb-0'),
                layout.Column('extra', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'is_active',
            get_form_button(
                button_title, delete, user=self.user, model='categorymodel',
                app='dashboard'
            )
        )


class AssetRequestModelForm(forms.ModelForm):
    class Meta:
        model = models.AssetRequest
        fields = (
            "asset", "requested", "details", "status",
            "request_date", "receive_date", "comment"
        )
        widgets = {
            'request_date': forms.DateInput(attrs={'type': "date"}),
            'receive_date': forms.DateInput(attrs={'type': "date"}),
            "details": forms.Textarea(attrs={'rows': 2}),
            "comment": forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['requested'].disabled = True
        self.fields['request_date'].disabled = True
        self.fields['details'].disabled = True
        self.helper = helper.FormHelper()
        button_title = "Save"
        delete = ""
        if self.instance.created_at:
            button_title = "Update"
            delete = self.instance
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column('asset', css_class='form-group col-md-6 mb-0'),
                layout.Column('status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('requested', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('request_date', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            'details',
            "comment",
            get_form_button(
                button_title, delete, user=self.user, model='categorymodel',
                app='dashboard'
            )
        )

    def clean(self):
        approved = models.AssetRequest.RequestStatus.APPROVED
        if (self.cleaned_data['status'] == approved):
            if self.cleaned_data['asset'] is None:
                self.add_error('asset', "Asset is required")
        return super().clean()


class AssetIssueModeForm(forms.ModelForm):
    class Meta:
        model = models.AssetIssue
        fields = (
            "asset", "status", "raised_by", "description", "fix_date",
            "resolved_date", "comment"
        )
        widgets = {
            'fix_date': forms.DateInput(attrs={'type': "date"}),
            'resolved_date': forms.DateInput(attrs={'type': "date"}),
            "description": forms.Textarea(attrs={'rows': 1}),
            "comment": forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['status'].queryset = models.AssetStatusModel.objects.filter(request=True)  # noqa
        self.fields['raised_by'].queryset = models.get_user_model().objects.all()  # noqa
        self.helper = helper.FormHelper()
        button_title = "Save"
        delete = ""
        if self.instance.created_at:
            button_title = "Update"
            delete = self.instance
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column('asset', css_class='form-group col-md-6 mb-0'),
                layout.Column('status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('raised_by', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('description', css_class='form-group col-md-6 mb-0'),  # noqa
            ),
            layout.Row(
                layout.Column('fix_date', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('resolved_date', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            "comment",
            get_form_button(
                button_title, delete, user=self.user, model='categorymodel',
                app='dashboard'
            )
        )
