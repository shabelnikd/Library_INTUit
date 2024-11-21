from rest_framework import serializers
from .models import Book, BookDirection, Comment, Genre, ViewsStats, News
from django.conf import settings

link = settings.LINK


class BookSerializer(serializers.ModelSerializer):
    # tender_dates = serializers.PrimaryKeyRelatedField(many=True, queryset=TenderDate.objects.all())
    # category_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())

    class Meta:
        model = Book
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'



class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['images'] = instance.get_image_url(f"image1")
        rep['genres'] = BookGenreSerializer(instance.genre).data
        rep['pdf'] = instance.get_pdf_url()
        rep['direction_name'] = DirectionSerializer(instance.direction).data
        rep['comments'] = CommentSerializer(instance.comments, many=True).data
        rep['stats'] = ViewsStatsSerializer(instance.view_stats, many=True).data
        rep['total_views'] = instance.view_stats.filter(v_count=True).count()
        rep['total_down'] = instance.view_stats.filter(d_count=True).count()
        if instance.author_account:
            rep['author_account'] = {
                'name': instance.author_account.full_name,
                'id': instance.author_account.id
            }

        return rep


class ViewsStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewsStats
        fields = ('user', )

    def to_representation(self, instance):
        from account.serializers import UserSimpleSerializer
        rep = super().to_representation(instance)
        rep['is_down'] = instance.d_count
        rep['is_view'] = instance.v_count
        rep['user'] = UserSimpleSerializer(instance.user).data
        return rep


class DirectionStatsSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = BookDirection
        fields = ('id', 'name', 'books_count')

    def get_books_count(self, obj):
        return obj.books.count()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('book', 'user')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['book'] = instance.book.id
        rep['user_id'] = instance.user.id
        rep['name'] = instance.user.full_name
        rep['phone'] = instance.user.phone_number
        return rep


class BookGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', )


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDirection
        fields = '__all__'



