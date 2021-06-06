import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class SetUpTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.creator = User.objects.create_user(username='test_creator')
        cls.viewer = User.objects.create_user(username='test_viewer')
        cls.follower = User.objects.create_user(username='test_follower')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.creator
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.creator,
            group=cls.group,
            image=image
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.viewer,
            text='Тестовый комментарий'
        )

        cls.post_kwargs = {
            'username': cls.post.author.username,
            'post_id': cls.post.id
        }

        cls.group_kwargs = {'slug': cls.group.slug}
        cls.creator_kwargs = {'username': cls.creator}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_viewer_client = Client()
        self.authorized_viewer_client.force_login(self.viewer)
        self.authorized_creator_client = Client()
        self.authorized_creator_client.force_login(self.creator)
        self.authorized_follower_client = Client()
        self.authorized_follower_client.force_login(self.follower)
