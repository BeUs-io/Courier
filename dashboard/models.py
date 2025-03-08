import random
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from core.base.model import BaseModel
from django.utils.translation import gettext as _


class CategoryModel(BaseModel):
    title = models.CharField(
        max_length=50, verbose_name=_("Title"), unique=True
    )
    description = models.TextField(
        null=True, blank=True, verbose_name=_("Description")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        db_table = 'category'
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        permissions = [("export_category", "Can Export Categories")]

    def __str__(self):
        if self.title:
            return self.title
        return "Unknown"

    def get_absolute_url(self):
        return reverse_lazy("category_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("category_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("category_form")

    @staticmethod
    def list_url():
        return reverse_lazy("category_list")


class DepartmentModel(BaseModel):
    title = models.CharField(
        max_length=50, verbose_name=_("Title"), unique=True
    )
    description = models.TextField(
        null=True, blank=True, verbose_name=_("Description")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        db_table = 'department'
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        permissions = [("export_department", "Can Export Department")]

    def __str__(self):
        if self.title:
            return self.title
        return "Unknown"

    def get_absolute_url(self):
        return reverse_lazy("department_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("department_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("department_form")

    @staticmethod
    def list_url():
        return reverse_lazy("department_list")


class SupplierModel(BaseModel):
    title = models.CharField(max_length=70, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    extra = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    def __str__(self):
        if self.title:
            return self.title
        return "Unknown"

    class Meta:
        db_table = 'supplier'
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        permissions = [("export_supplier", "Can Export Suppliers")]

    def get_absolute_url(self):
        return reverse_lazy("supplier_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("supplier_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("supplier_form")

    @staticmethod
    def list_url():
        return reverse_lazy("supplier_list")


class AssetStatusModel(BaseModel):
    title = models.CharField(max_length=30, unique=True)
    color = models.CharField(max_length=10, null=True, blank=True)
    request = models.BooleanField(
        default=False, verbose_name="For Request Status",
        help_text="show on request status"
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    def get_absolute_url(self):
        return reverse_lazy("asset_status_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("asset_status_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("asset_status_new")

    @staticmethod
    def list_url():
        return reverse_lazy("asset_status_list")

    class Meta:
        db_table = 'asset_status'
        verbose_name = _("Asset Status")
        verbose_name_plural = _("Asset Status")
        permissions = [("export_asset_status", "Can Export Asset Status")]

    def __str__(self):
        if self.title:
            return self.title
        return "Unknown"


class AssetModel(BaseModel):
    asset_id = models.CharField(
        max_length=16, verbose_name=_("Asset ID"), unique=True
    )
    title = models.CharField(max_length=150, verbose_name=_("Title"))
    model = models.CharField(
        max_length=25, null=True, blank=True, verbose_name=_("Model")
    )
    description = models.TextField(
        null=True, blank=True, verbose_name=_("Description")
    )
    price = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("Price"), null=True, blank=True
    )
    asset_status = models.ForeignKey(
        to=AssetStatusModel, on_delete=models.SET_NULL, null=True, blank=True
    )
    category = models.ManyToManyField(
        to=CategoryModel, related_name="category_asset", blank=True
    )
    supplier = models.ForeignKey(
        to=SupplierModel, on_delete=models.CASCADE, null=True,
        blank=True, related_name="supplier_asset"
    )
    department = models.ManyToManyField(
        to=DepartmentModel, related_name="department_asset", blank=True
    )
    image = models.ImageField(
        upload_to="asset/image/", null=True, blank=True,
        verbose_name=_("Image")
    )
    receipt = models.ImageField(
        upload_to="asset/receipt/image/", null=True, blank=True,
        verbose_name=_("Asset Receipt")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    added_by = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE,
        related_name="asset_added_by"
    )

    def get_absolute_url(self):
        return reverse_lazy("asset_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("asset_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("asset_form")

    @staticmethod
    def list_url():
        return reverse_lazy("asset_list")

    @classmethod
    def get_asset_id(cls):
        number = random.randint(1000000, 9999999)
        if cls._meta.model.objects.filter(asset_id=f"AST-{number}").exists():
            return cls.get_asset_id()
        return f"AST-{number}"

    def get_employees(self):
        employees = "None"
        return employees

    def get_category(self):
        category = ",".join([cate.title for cate in self.category.all()])
        if category:
            return category
        return "None"

    def get_departments(self):
        departments = ",".join(
            [department.title for department in self.department.all()]
        )
        if not departments:
            departments = "None"
        return departments

    def __str__(self):
        if self.title:
            return self.title
        return "Unknown"

    class Meta:
        db_table = 'asset'
        verbose_name = _("Asset")
        verbose_name_plural = _("Assets")
        permissions = [("export_asset", "Can Export Asset")]


class AssetRequest(BaseModel):
    class RequestStatus(models.IntegerChoices):
        PENDING = 1, "Pending"
        PROGRESS = 2, "In Progress"
        REJECTED = 3, "Rejected"
        APPROVED = 4, "Approved"
        IN_USE = 5, "In Use"
        AVAILABLE = 6, "Available"
        DAMAGE = 7, "Damage"
        RETURN = 8, "Return"
        EXPIRED = 9, "Expired"
        Required_License_Update = 10, "Required License Update"

    asset = models.ForeignKey(
        to=AssetModel, on_delete=models.CASCADE,
        null=True, blank=True
    )
    requested = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE,
        related_name="requested_user"
    )
    approved_by = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE,
        related_name="approved_user", null=True, blank=True
    )
    details = models.TextField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        choices=RequestStatus.choices, default=RequestStatus.PENDING
    )
    request_date = models.DateTimeField(
        auto_now_add=False, null=True, blank=True
    )
    receive_date = models.DateTimeField(
        auto_now_add=False, null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.asset:
            return f"{self.asset.title} Requested by {self.requested}"
        else:
            return f"asset Requested by {self.requested}"

    def get_status(self):
        title = self.get_status_display()
        if self.status == 1:
            return f'<span class="badge bg-info">{title}</span>'
        elif self.status == 2:
            return f'<span class="badge bg-success">{title}</span>'
        elif self.status == 3:
            return f'<span class="badge bg-danger">{title}</span>'
        elif self.status == 4:
            return f'<span class="badge bg-primary">{title}</span>'
        else:
            return f'<span class="badge bg-light text-black">{title}</span>'

    class Meta:
        db_table = 'asset_request'
        verbose_name = _("Asset Request")
        verbose_name_plural = _("Asset Request")
        permissions = [("export_assetrequest", "Can Export Asset Request")]

    def get_absolute_url(self):
        return reverse_lazy("asset_request_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("asset_request_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return "/"

    @staticmethod
    def list_url():
        return reverse_lazy("asset_request_list")


class AssetIssue(BaseModel):
    asset = models.ForeignKey(to=AssetModel, on_delete=models.CASCADE)
    status = models.ForeignKey(AssetStatusModel, on_delete=models.CASCADE)
    raised_by = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE,
        related_name="raised_user"
    )
    description = models.TextField(null=True, blank=True)
    fix_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    resolved_date = models.DateTimeField(
        auto_now_add=False, null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.asset.title} Requested by {self.raised_by}"

    class Meta:
        db_table = 'asset_issue'
        verbose_name = _("Asset Issue")
        verbose_name_plural = _("Asset Issue")
        permissions = [("export_assetissue", "Can Export Asset Issue")]

    def get_absolute_url(self):
        return reverse_lazy("asset_issue_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("asset_issue_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("asset_issue_form")

    @staticmethod
    def list_url():
        return reverse_lazy("asset_issue_list")
