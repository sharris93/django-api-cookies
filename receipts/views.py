from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Receipt, ReceiptItem
from .permissions import IsReceiptOwner
from .filters import ReceiptFilter, ReceiptItemFilter
from .mixins import OwnerQuerySetMixin
from .serializers.common import (
    ReceiptListSerializer,
    ReceiptDetailSerializer,
    ReceiptItemSerializer,
    ReceiptItemBulkSerializer,
)

# --- Receipts

class ReceiptListCreateView(OwnerQuerySetMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReceiptFilter

    def get_queryset(self):
        # Users can only see their own receipts
        return Receipt.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ReceiptListSerializer
        return ReceiptDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReceiptDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsReceiptOwner]
    serializer_class = ReceiptDetailSerializer
    queryset = Receipt.objects.prefetch_related("items")


# --- ReceiptItems (nested) ---

class ReceiptItemListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReceiptItemFilter

    def get_queryset(self):
        receipt = get_object_or_404(
            Receipt,
            id=self.kwargs["receipt_id"],
            owner=self.request.user
        )
        return ReceiptItem.objects.filter(receipt=receipt)

    def perform_create(self, serializer):
        receipt = get_object_or_404(
            Receipt,
            id=self.kwargs["receipt_id"],
            owner=self.request.user
        )
        serializer.save(receipt=receipt)


class ReceiptItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsReceiptOwner]
    serializer_class = ReceiptItemSerializer

    def get_queryset(self):
        receipt = get_object_or_404(
            Receipt,
            id=self.kwargs["receipt_id"],
            owner=self.request.user
        )
        return ReceiptItem.objects.filter(receipt=receipt)


# --- Bulk Replace Items ---

class ReceiptItemBulkReplaceView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, receipt_id):
        receipt = get_object_or_404(
            Receipt,
            id=receipt_id,
            owner=request.user
        )

        serializer = ReceiptItemBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items_data = serializer.validated_data["items"]

        with transaction.atomic():
            receipt.items.all().delete()
            ReceiptItem.objects.bulk_create([
                ReceiptItem(receipt=receipt, **item) for item in items_data
            ])

        return Response(
            {"detail": "Items replaced successfully."},
            status=status.HTTP_200_OK
        )
