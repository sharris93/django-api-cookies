from django.urls import path
from .views import (
    ReceiptListCreateView,
    ReceiptDetailView,
    ReceiptItemListCreateView,
    ReceiptItemDetailView,
    ReceiptItemBulkReplaceView
)

urlpatterns = [
    path(
        "",
        ReceiptListCreateView.as_view(),
        name="receipt-list"
    ),
    path(
        "<int:pk>/",
        ReceiptDetailView.as_view(),
        name="receipt-detail"
    ),

    path(
        "<int:receipt_id>/items/",
        ReceiptItemListCreateView.as_view(),
        name="receipt-item-list"
    ),
    path(
        "<int:receipt_id>/items/<int:pk>/",
        ReceiptItemDetailView.as_view(),
        name="receipt-item-detail"
    ),

    path(
        "<int:receipt_id>/items/bulk_replace/",
        ReceiptItemBulkReplaceView.as_view(),
        name="receipt-item-bulk-replace"
    ),
]
