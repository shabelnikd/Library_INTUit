from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from event.models import Favorite, Book
from .models import Group
from .tasks import send_activation_mail

AbstractUser = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = ('email', 'full_name', 'password', 'phone_number',
                  'user_type')

    def create(self, validated_data):
        user = AbstractUser.objects.create_user(**validated_data)
        user.create_activation_code()
        send_activation_mail(user.email, user.activation_code)
        return user


class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, required=True)

    def validate_email(self, email):
        if not AbstractUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не зарегистрирован')
        return email

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.pop('password')
        user = AbstractUser.objects.get(email=email)

        if not user.check_password(password):
            raise serializers.ValidationError('Неверный пароль')
        if not user.is_active:
            raise serializers.ValidationError('Активируйте свою учетную запись через email')
        if not user:
            raise serializers.ValidationError('Пользователь не найден (Непредвиденная ошибка)')

        refresh = self.get_token(user)

        attrs['user_id'] = user.id
        attrs['user_type'] = user.user_type
        attrs['full_name'] = user.full_name

        if user.user_type != 'teacher':
            attrs['group'] = user.group.name
            attrs['course'] = user.group.course
            attrs['direction'] = user.group.direction

        attrs['phone_number'] = user.phone_number
        attrs['tokens'] = {'access': str(refresh.access_token), 'refresh': str(refresh)}

        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not AbstractUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Такого пользователя не существует')
        return email


class CreateNewPasswordSerializer(serializers.Serializer):
    activation_code = serializers.CharField(required=True)
    password = serializers.CharField(min_length=6, required=True)

    def validate_activation_code(self, code):
        if not AbstractUser.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('Активационный код введен неверно')
        return code

    def create_pass(self):
        code = self.validated_data.get('activation_code')
        password = self.validated_data.get('password')
        user = AbstractUser.objects.get(activation_code=code)
        user.set_password(password)
        user.activation_code = ''
        user.save()


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = 'password'

    def set_new_password(self):
        user = self.instance
        user.set_password(self.validated_data['password'])
        user.save()


class FavoriteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('book',)

    def to_representation(self, instance):
        from event.serializers import BookListSerializer
        rep = super().to_representation(instance)
        rep['book'] = BookListSerializer(Book.objects.get(id=instance.book_id)).data
        return rep


class UserStatsSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = AbstractUser
        fields = ('id', 'full_name', 'email', 'phone_number', 'books_count')

    def get_books_count(self, obj):
        return obj.books.all().count()


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = ('id', 'email', 'full_name', 'phone_number',
                  'user_type', 'group', 'is_staff')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user_id'] = instance.id
        rep['email'] = instance.email
        rep['full_name'] = instance.full_name

        if instance.user_type != 'teacher':
            rep['group'] = instance.group.name
            rep['course'] = instance.group.course
            rep['direction'] = instance.group.direction
            rep['fav'] = FavoriteListSerializer(instance.favorites.all(), many=True).data
        elif instance.user_type == 'teacher':
            from event.serializers import BookListSerializer
            rep['user_books'] = BookListSerializer(instance.books.all(), many=True).data
            rep['is_staff'] = instance.is_staff

        rep['phone_number'] = instance.phone_number

        return rep


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = ('id', 'email', 'full_name', 'phone_number',
                  'user_type', 'group')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user_id'] = instance.id
        rep['email'] = instance.email
        rep['full_name'] = instance.full_name

        if instance.user_type != 'teacher':
            rep['group'] = instance.group.name
            rep['course'] = instance.group.course
            rep['direction'] = instance.group.direction

        return rep


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

