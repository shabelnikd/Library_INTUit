from random import sample

from rest_framework.generics import ListAPIView
from rest_framework.viewsets import GenericViewSet
from . import serializers
from .paginator import EventPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TenderFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsAuthor
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import Book, Favorite, Comment, BookDirection, Genre, ViewsStats
from rest_framework import status, mixins, viewsets
from drf_yasg.utils import swagger_auto_schema

from .serializers import DirectionStatsSerializer


# from django.db.models import Q


class BookViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'random', 'delete_cp']:
            return serializers.BookListSerializer
        return serializers.BookSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'random', 'delete_cp']:
            return [AllowAny()]
        if self.action in ['update_book', 'delete_book']:
            return [IsAuthor()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Book.objects.all()
        # card_type = self.request.query_params.get('genre')
        # filters = Q()
        # queryset = queryset.select_related('author')
        # if card_type:
        #     filters &= Q(card_type=card_type)
        # queryset = queryset.filter(filters)

        return queryset

    @swagger_auto_schema()
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = Book.objects.get(id=kwargs.get('pk'))
            return Response(serializers.BookListSerializer(obj).data)
        except Book.DoesNotExist:
            return Response('Not Found', status=404)

    @action(detail=False, methods=['GET'])
    def random(self, request):
        queryset = Book.objects.all().order_by('?')  # Случайная сортировка
        random_books = sample(list(queryset), min(6, len(queryset)))  # 8 или максимально доступное количество книг
        serializer = self.get_serializer(random_books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    @swagger_auto_schema(request_body=serializers.BookSerializer())
    def create_book(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)

        author = request.data.get('author')
        title = request.data.get('title')
        description = request.data.get('description')
        pages = request.data.get('pages')
        year = request.data.get('year')
        pdf = request.data.get('pdf')
        image1 = request.data.get('image1')
        genre = request.data.get('genre')
        Genre.objects.get_or_create(name=genre)
        author_id = request.user.id
        direction = get_object_or_404(BookDirection, name=request.data.get('direction'))

        book = Book.objects.create(
            author=author, title=title, description=description,
            direction=direction, pages=pages,
            year=year, pdf=pdf, image1=image1, author_account_id=author_id,
            genre=get_object_or_404(Genre, name=genre)
        )

        return Response(serializers.BookListSerializer(book).data, status=201)

    @action(detail=True, methods=['delete'])
    def delete_book(self, request, pk=None):
        try:
            tender = Book.objects.get(pk=pk)
            self.check_object_permissions(request, tender)
            tender.delete()
            return Response({'success': 'Event deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Book.DoesNotExist:
            return Response({'error': 'Event does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['GET'])
    def add_favorite(self, request, pk):
        if not request.user.is_authenticated:
            return Response(status=401)
        book = get_object_or_404(Book, id=pk)
        if Favorite.objects.filter(user=request.user, book=book).exists():
            Favorite.objects.filter(user=request.user, book=book).delete()
            return Response('удалено')
        else:
            Favorite.objects.create(user=request.user, book=book)
        return Response('сохранено', status=201)

    @action(detail=True, methods=['POST'])
    def comment(self, request, pk):
        if not request.user.is_authenticated:
            return Response(status=401)

        user = self.request.user
        book = get_object_or_404(Book, id=pk)
        text = request.data.get('text')

        Comment.objects.create(user=user, book=book, text=text)

        return Response('Комментарий добавлен', status=201)

    @action(detail=True, methods=['GET'])
    def add_view(self, request, pk):
        if not request.user.is_authenticated:
            return Response(status=401)
        if request.user.user_type == 'teacher':
            return Response(status=204)
        book = get_object_or_404(Book, id=pk)
        if ViewsStats.objects.filter(user=request.user, book=book).exists():
            stats = ViewsStats.objects.get(user=request.user, book=book)
            stats.v_count = True
            stats.save()
            return Response(status=204)
        else:
            ViewsStats.objects.create(user=request.user, book=book, v_count=True)
        return Response('OK', status=201)

    @action(detail=True, methods=['GET'])
    def add_down(self, request, pk):
        if not request.user.is_authenticated:
            return Response(status=401)
        if request.user.user_type == 'teacher':
            return Response(status=204)
        book = get_object_or_404(Book, id=pk)
        if ViewsStats.objects.filter(user=request.user, book=book).exists():
            stats = ViewsStats.objects.get(user=request.user, book=book)
            stats.d_count = True
            stats.save()
            return Response(status=204)
        else:
            ViewsStats.objects.create(user=request.user, book=book, d_count=True)
        return Response('OK', status=201)

    @action(detail=False, methods=['GET'])
    def delete_cp(self, request):
        books = Book.objects.filter(title__in=Book.objects.values_list('title', flat=True).distinct())
        serializer = self.get_serializer(books, many=True)

        books.delete()
        return Response(serializer.data)




class DirectionStatsViewSet(viewsets.ModelViewSet):
    queryset = BookDirection.objects.all()
    serializer_class = DirectionStatsSerializer

