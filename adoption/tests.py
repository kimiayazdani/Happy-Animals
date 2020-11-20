from rest_framework.test import force_authenticate, APIRequestFactory
from django.test import TestCase
from account_management.models import Account
from adoption.views import PostView
from adoption.models import Post


class TestPostViewSet(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        user = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': 'TestUser123'
        }
        self.user = Account.objects.create_user(**user)
        self.post = Post.objects.create(
            title='test',
            description='test description',
            kind='dog',
            author=self.user,
            tags=['test_tag']
        )

    def test_create_post(self):
        request = self.factory.post(
            'api/v1/adoption/post/',
            data={
                'title': 'create post test',
                'description': 'testtest123',
                'kind': 'cat',
                'tags': ['tag1', 'tag2']
            },
            format='json'
        )
        view = PostView.as_view({'post': 'create'})
        force_authenticate(request, self.user)
        res = view(request)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['kind'], 'cat')
        self.assertListEqual(res.data['tags'], ['tag1', 'tag2'])

    def test_get_post(self):
        request = self.factory.get(
            'api/v1/adoption/post/',
        )
        view = PostView.as_view({'get': 'retrieve'})
        force_authenticate(request, self.user)
        res = view(request, pk=self.post.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['kind'], 'dog')
        self.assertListEqual(res.data['tags'], ['test_tag'])

    def test_update_post(self):
        request = self.factory.patch(
            'api/v1/adoption/post/',
            data={
                'title': 'new title',
                'kind': 'hamster'
            },
            format='json'
        )
        view = PostView.as_view({'patch': 'partial_update'})
        force_authenticate(request, self.user)
        res = view(request, pk=self.post.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['kind'], 'hamster')
        self.assertEqual(res.data['title'], 'new title')
