from rest_framework.permissions import BasePermission
from receipts.models import Receipt, ReceiptItem

class IsReceiptOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Receipt):
            return obj.owner == request.user

        if isinstance(obj, ReceiptItem):
            return obj.receipt.owner == request.user

        return False
