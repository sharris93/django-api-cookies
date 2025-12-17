import django_filters
from .models import Receipt, ReceiptItem

# --- Receipt Filters

class ReceiptFilter(django_filters.FilterSet):
    # Tags filter: OR / AND mode
    tags = django_filters.CharFilter(method="filter_tags")

    # Date range filters
    date_before = django_filters.DateFilter(field_name="datetime_parsed", lookup_expr="lte")
    date_after = django_filters.DateFilter(field_name="datetime_parsed", lookup_expr="gte")

    # Numeric filters
    total_min = django_filters.NumberFilter(field_name="total_price", lookup_expr="gte")
    total_max = django_filters.NumberFilter(field_name="total_price", lookup_expr="lte")

    # Text filters
    store_name = django_filters.CharFilter(field_name="store_name", lookup_expr="icontains")
    store_city = django_filters.CharFilter(field_name="store_city", lookup_expr="icontains")
    store_country = django_filters.CharFilter(field_name="store_country", lookup_expr="icontains")
    payment_method = django_filters.CharFilter(field_name="payment_method", lookup_expr="icontains")

    class Meta:
        model = Receipt
        fields = [
            "tags",
            "date_before", "date_after",
            "total_min", "total_max",
            "store_name", "store_city", "store_country",
            "payment_method",
        ]

    # Tags filter method
    def filter_tags(self, queryset, name, value):
        tags_list = [t.strip() for t in value.split(",") if t.strip()]
        if not tags_list:
            return queryset
        mode = self.request.GET.get("tags_mode", "any").lower()
        if mode == "all":
            for t in tags_list:
                queryset = queryset.filter(items__tags__contains=[t])
        else:
            queryset = queryset.filter(items__tags__overlap=tags_list)
        return queryset.distinct()


# --- ReceiptItem Filters

class ReceiptItemFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(field_name="description", lookup_expr="icontains")
    price_min = django_filters.NumberFilter(field_name="total_price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="total_price", lookup_expr="lte")
    tags = django_filters.CharFilter(method="filter_tags")

    class Meta:
        model = ReceiptItem
        fields = []

    def filter_tags(self, queryset, name, value):
        tags_list = [t.strip() for t in value.split(",") if t.strip()]
        if not tags_list:
            return queryset
        mode = self.request.GET.get("tags_mode", "any").lower()
        if mode == "all":
            for t in tags_list:
                queryset = queryset.filter(tags__contains=[t])
        else:
            queryset = queryset.filter(tags__overlap=tags_list)
        return queryset.distinct()
