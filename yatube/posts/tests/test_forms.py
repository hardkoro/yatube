from django.urls import reverse

from .setup_tests import SetUpTests
from posts.models import Post


class NewPostFormTests(SetUpTests):
    def test_new_post(self):
        """Валидная форма создаёт запись в Post."""
        posts_count = Post.objects.count()

        form_data = {'text': 'Тестовый пост'}
        response = self.authorized_creator_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        TEXT_AFTER_EDIT = 'Новая запись'

        post = Post.objects.create(
            text='Тестовая запись',
            author=self.creator
        )

        posts_count = Post.objects.count()

        form_data = {'text': TEXT_AFTER_EDIT}
        self.authorized_creator_client.post(
            reverse('post_edit', kwargs={
                'username': self.creator, 'post_id': post.id}),
            data=form_data
        )

        post = Post.objects.get(pk=post.id)
        self.assertEqual(post.text, TEXT_AFTER_EDIT)
        self.assertEqual(Post.objects.count(), posts_count)
