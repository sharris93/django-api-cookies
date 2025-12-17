# receipts/serializers.py
from rest_framework import serializers
from django.utils.dateparse import parse_datetime
from ..models import Receipt, ReceiptItem

class ReceiptItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptItem
        fields = [
            "id",
            "description",
            "raw_entry",
            "quantity",
            "price_per_unit",
            "total_price",
            "tags",
        ]
        # read_only_fields = ["id"]

class ReceiptListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = [
            "id",
            "store_name",
            "store_city",
            "store_country",
            "datetime_parsed",
            "total_price",
            "currency_primary",
            "created_at",
        ]



class ReceiptDetailSerializer(serializers.ModelSerializer):
    items = ReceiptItemSerializer(many=True)

    class Meta:
        model = Receipt
        fields = [
            "id",

            "datetime_raw",
            "datetime_iso_8601",
            "datetime_timezone",
            "datetime_parsed",

            "currency_primary",
            "currency_secondary",
            "currency_exchange_rate",
            "currency_symbol",

            "store_name",
            "store_street",
            "store_number",
            "store_zip",
            "store_city",
            "store_country",

            "total_subtotal",
            "total_tax",
            "total_price",

            "payment_method",
            "items",
        ]
        read_only_fields = ["datetime_parsed"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])

        # auto-parse ISO 8601 string
        iso = validated_data.get("datetime_iso_8601")
        validated_data["datetime_parsed"] = parse_datetime(iso) if iso else None

        receipt = Receipt.objects.create(**validated_data)

        ReceiptItem.objects.bulk_create([
            ReceiptItem(receipt=receipt, **item)
            for item in items_data
        ])

        return receipt

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        # update receipt fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        iso = validated_data.get("datetime_iso_8601")
        if iso:
            instance.datetime_parsed = parse_datetime(iso)

        instance.save()

        # optional: full replace of items
        if items_data is not None:
            instance.items.all().delete()
            ReceiptItem.objects.bulk_create([
                ReceiptItem(receipt=instance, **item)
                for item in items_data
            ])

        return instance

class ReceiptItemBulkSerializer(serializers.Serializer):
    items = ReceiptItemSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("At least one item is required.")
        return items
