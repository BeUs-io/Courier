# Generated by Django 5.0.1 on 2024-05-31 09:19

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetStatusModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('title', models.CharField(max_length=30, unique=True)),
                ('color', models.CharField(blank=True, max_length=10, null=True)),
                ('request', models.BooleanField(default=False, help_text='show on request status', verbose_name='For Request Status')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Asset Status',
                'verbose_name_plural': 'Asset Status',
                'db_table': 'asset_status',
                'permissions': [('export_asset_status', 'Can Export Asset Status')],
            },
        ),
        migrations.CreateModel(
            name='CategoryModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('title', models.CharField(max_length=50, unique=True, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'db_table': 'category',
                'permissions': [('export_category', 'Can Export Categories')],
            },
        ),
        migrations.CreateModel(
            name='DepartmentModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('title', models.CharField(max_length=50, unique=True, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
                'db_table': 'department',
                'permissions': [('export_department', 'Can Export Department')],
            },
        ),
        migrations.CreateModel(
            name='SupplierModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('title', models.CharField(max_length=70, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=30, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('extra', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Supplier',
                'verbose_name_plural': 'Suppliers',
                'db_table': 'supplier',
                'permissions': [('export_supplier', 'Can Export Suppliers')],
            },
        ),
        migrations.CreateModel(
            name='AssetModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('asset_id', models.CharField(max_length=16, unique=True, verbose_name='Asset ID')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('model', models.CharField(blank=True, max_length=25, null=True, verbose_name='Model')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('price', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Price')),
                ('image', models.ImageField(blank=True, null=True, upload_to='asset/image/', verbose_name='Image')),
                ('receipt', models.ImageField(blank=True, null=True, upload_to='asset/receipt/image/', verbose_name='Asset Receipt')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_added_by', to=settings.AUTH_USER_MODEL)),
                ('asset_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.assetstatusmodel')),
                ('category', models.ManyToManyField(blank=True, related_name='category_asset', to='dashboard.categorymodel')),
                ('department', models.ManyToManyField(blank=True, related_name='department_asset', to='dashboard.departmentmodel')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_asset', to='dashboard.suppliermodel')),
            ],
            options={
                'verbose_name': 'Asset',
                'verbose_name_plural': 'Assets',
                'db_table': 'asset',
                'permissions': [('export_asset', 'Can Export Asset')],
            },
        ),
        migrations.CreateModel(
            name='AssetRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('details', models.TextField(blank=True, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'In Progress'), (3, 'Rejected'), (4, 'Approved'), (5, 'In Use'), (6, 'Available'), (7, 'Damage'), (8, 'Return'), (9, 'Expired'), (10, 'Required License Update')], default=1)),
                ('request_date', models.DateTimeField(blank=True, null=True)),
                ('receive_date', models.DateTimeField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved_user', to=settings.AUTH_USER_MODEL)),
                ('asset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.assetmodel')),
                ('requested', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Asset Request',
                'verbose_name_plural': 'Asset Request',
                'db_table': 'asset_request',
                'permissions': [('export_assetrequest', 'Can Export Asset Request')],
            },
        ),
        migrations.CreateModel(
            name='AssetIssue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('description', models.TextField(blank=True, null=True)),
                ('fix_date', models.DateTimeField(blank=True, null=True)),
                ('resolved_date', models.DateTimeField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('raised_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raised_user', to=settings.AUTH_USER_MODEL)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.assetmodel')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.assetstatusmodel')),
            ],
            options={
                'verbose_name': 'Asset Issue',
                'verbose_name_plural': 'Asset Issue',
                'db_table': 'asset_issue',
                'permissions': [('export_assetissue', 'Can Export Asset Issue')],
            },
        ),
    ]
