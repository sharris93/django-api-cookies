# receipts/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex



class Receipt(models.Model):
    # ownership
    owner = models.ForeignKey(
        to='users.User',
        related_name='receipts_owned',
        on_delete=models.CASCADE
    )

    # datetime
    datetime_raw = models.CharField(max_length=64)
    datetime_iso_8601 = models.CharField(max_length=64)
    datetime_timezone = models.CharField(max_length=64)
    datetime_parsed = models.DateTimeField(null=True, blank=True)

    # currency
    currency_primary = models.CharField(max_length=32)
    currency_secondary = models.CharField(max_length=16, blank=True, null=True)
    currency_exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    currency_symbol = models.CharField(max_length=8)

    # store
    store_name = models.CharField(max_length=255)
    store_street = models.CharField(max_length=255, blank=True, null=True)
    store_number = models.CharField(max_length=64, blank=True, null=True)
    store_zip = models.CharField(max_length=32, blank=True, null=True)
    store_city = models.CharField(max_length=255)
    store_country = models.CharField(max_length=255)

    # totals
    total_subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # misc
    payment_method = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.id} - {self.store_name}: {self.total_price}"
    

class ReceiptItem(models.Model):
    receipt = models.ForeignKey(
        Receipt, related_name="items", on_delete=models.CASCADE
    )

    description = models.CharField(max_length=255)
    raw_entry = models.CharField(max_length=255)

    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    tags = ArrayField(models.CharField(max_length=64), default=list, blank=True)

    class Meta:
        indexes = [
            GinIndex(fields=["tags"]),
        ]


    def __str__(self):
        return f"{self.description}"
