from django_filters import rest_framework as filters
from .models import Book


class TenderFilter(filters.FilterSet):
    search = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['search']
