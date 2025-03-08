from django.urls import path
from assetdash import views


urlpatterns = [
    path('assetdash/', views.AssetDashboard.as_view(), name='assetdash'),
    path(
        'assetdash/asset/list/',
        views.AssetListView.as_view(),
        name="assetdash_asset_list"
    ),
    path(
        'assetdash/request/list/',
        views.AssetRequestListView.as_view(),
        name="assetdash_request_list"
    ),
    path(
        'assetdash/request/create/',
        views.AssetRequestCreateView.as_view(),
        name="assetdash_request_create"
    ),
    path(
        'assetdash/request/update/<pk>/',
        views.AssetRequestUpdateView.as_view(),
        name="assetdash_request_update"
    ),
    path(
        'assetdash/issue/list/',
        views.AssetIssueListView.as_view(),
        name="assetdash_issue_list"
    )
]
