class OwnerQuerySetMixin:
    """
    Filters queryset to objects owned by request.user
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
