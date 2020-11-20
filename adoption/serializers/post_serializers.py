from rest_framework import serializers
from adoption.models import Comment, Post
from collections import OrderedDict
from account_management.models import Account
from django.db import transaction


#
# class LikeSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField()
#     username = serializers.CharField()
#     email = serializers.CharField()
#
#     class Meta:
#         model = Account
#         fields = ['id', 'username', 'email']


class PostSerializer(serializers.ModelSerializer):
    """
    this serializer used for POST request
    """
    kind = serializers.CharField(default=Post.KIND_DOG)
    author = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = [
            'id', 'kind', 'title', 'description', 'author',
            'tags', 'pet_image'
        ]
        read_only_fields = ('id', )

    def get_user_id(self):
        return self.context['user_id']

    def validate(self, attrs):
        id = self.get_user_id()
        attrs['author'] = Account.objects.get(id=id)
        return attrs

    def create(self, validated_data):
        post = Post.objects.create(
            **validated_data
        )
        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    """
        this serializer used for PATCH request
    """

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'description',
            'kind',
            'tags',
            'pet_image',
        )
        writable_fields = ('title', 'description', 'tags', 'tags_image', 'kind')

    def update(self, instance: Post, validated_data):
        with transaction.atomic():
            for field in self.Meta.writable_fields:
                if field in validated_data:
                    setattr(instance, field, validated_data[field])
            instance.save()
            return super(PostUpdateSerializer, self).update(instance, validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """
        this serializer used for GET request with action:list
    """
    tags = serializers.ListField()
    author__username = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Post
        context_fields = (
            'id',
            'title',
            'author__username',
            'tags',
            'pet_image',
        )
        fields = context_fields
        read_only_fields = context_fields

    def to_representation(self, instance):

        ret = OrderedDict()
        fields = self.Meta.context_fields
        for field in fields:
            if field in self.Meta.fields:
                ret[field] = self.context['data'][instance['id']][field]
        return ret
