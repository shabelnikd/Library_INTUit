from django.contrib import admin
from .models import *

admin.site.register(Favorite)
admin.site.register(Comment)
admin.site.register(BookDirection)
admin.site.register(ViewsStats)
admin.site.register(News)

@admin.action(description="Delete copies")
def delete_cp(self, request, queryset):
     books = Book.objects.filter(title__in=Book.objects.values_list('title', flat=True).distinct())
     books.delete()
     books.save()

@admin.action(description="Danoni All")
def danoni(self, request, queryset):
    queryset.update(author_account_id=1)


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_account']
    search_fields = ['title', 'author_account__full_name']
    list_filter = ('author_account',)
    actions = [delete_cp, danoni]


admin.site.register(Book, BookAdmin)

admin.site.register(Genre)
