import logging
from rest_framework.permissions import IsAuthenticated
from django_plus.api import UrlParam as _p
from adoption.serializers.post_serializers import (
    PostSerializer,
    PostUpdateSerializer,
    PostListSerializer
)
from adoption.models import Post
from datetime import datetime, timedelta
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from django.conf import settings

logger = logging.getLogger(__name__)


class PostView(ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    filter_backends = (DjangoFilterBackend,)
    list_params_template = [
        _p('start', _p.datetime, default=datetime.now() - timedelta(days=90)),
        _p('end', _p.datetime, default=datetime.now()),
        _p('kinds', _p.list(separator=',', item_cleaner=_p.string)),
        _p('tags', _p.list(separator=',', item_cleaner=_p.string))
    ]

    def get_serializer_class(self):
        if self.request.method == 'GET' and self.action == 'list':
            return PostListSerializer
        elif self.request.method == 'PATCH':
            return PostUpdateSerializer
        return PostSerializer

    def get_serializer_context(self):
        if self.request.method == 'GET' and self.action == 'list':
            context = {
                'data': self.get_data(),
                'view': self,
            }
        else:
            context = {
                'user_id': self.request.user.id,
            }
        return context

    def get_data(self):
        data = self.get_queryset()
        data = {d['id']: d for d in data}
        return data

    def get_queryset(self):
        _query = None
        if self.request.method == 'GET' and self.action == 'list':
            params = _p.clean_data(self.request.query_params, self.list_params_template)
            start = params['start']
            end = params['end']
            kinds = params['kinds']
            tags = params['tags']
            validation_kinds = self.validate_kinds(kinds)
            if start > end:
                raise ValidationError('start datetime should be before end datetime')
            if not validation_kinds:
                raise ValidationError('kind should be in cat, dog or hamster ')
            _query = Post.objects.filter(
                created__gte=start, created__lte=end,
            )
            if kinds:
                _query = _query.filter(kind__in=kinds)
            if tags:
                _query = _query.filter(tags__overlap=tags)
            _query = _query.values(
                'id', 'kind', 'title', 'tags', 'description', 'author__username', 'pet_image'
            )

        elif self.request.method == 'PATCH':
            _query = Post.objects.all()
        _query = self.slice_queryset(_query)

        return _query

    @staticmethod
    def validate_kinds(kinds):
        if kinds is None:
            return True
        for kind in kinds:
            if kind not in Post.KINDS:
                return False
        return True

    def slice_queryset(self, queryset):
        offset = self.request.query_params.get('offset', 0)
        limit = self.request.query_params.get('limit', None)
        if limit is not None:
            return queryset[int(offset):int(limit)]
        return queryset

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response(data={'object with id:{} does not exist'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        comments = []
        for comment in post.comments.all():
            comments.append(comment.author.username)
        if post.pet_image:
            image_src = str(post.pet_image) + settings.MEDIA_URL
        else:
            image_src = None
        data = {
            'id': pk,
            'title': post.title,
            'start': post.description,
            'created': post.created,
            'tags': post.tags,
            'author': post.tags,
            'comments': comments,
            'pet_image': image_src,
            'kind': post.kind
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response(data={'object with id:{} does not exist'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(post)
        return Response(data={'object deleted successfully'}, status=status.HTTP_200_OK)
