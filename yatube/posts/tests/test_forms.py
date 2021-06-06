from django.urls import reverse

from posts.models import Comment, Post

from .setup_tests import SetUpTests


class ModelFormsTests(SetUpTests):
    def test_add_record(self):
        """Валидная форма создаёт запись."""
        model_params = {
            (reverse('new_post'), reverse('index'), Post),
            (reverse('add_comment', kwargs=self.post_kwargs),
             reverse('post', kwargs=self.post_kwargs), Comment),
            (reverse('post', kwargs=self.post_kwargs),
             reverse('post', kwargs=self.post_kwargs), Comment)
        }

        for post_url, redirect_url, model in model_params:
            with self.subTest(model=model):
                rec_count = model.objects.count()
                form_data = {'text': 'Тест'}

                response = self.authorized_creator_client.post(
                    post_url, data=form_data, follow=True
                )

                self.assertRedirects(response, redirect_url)
                self.assertEqual(model.objects.count(), rec_count + 1)


class PostFormTests(SetUpTests):
    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        TEXT_AFTER_EDIT = 'Новая запись'

        posts_count = Post.objects.count()

        form_data = {'text': TEXT_AFTER_EDIT}
        self.authorized_creator_client.post(
            reverse('post_edit', kwargs=self.post_kwargs),
            data=form_data
        )

        post = Post.objects.get(pk=self.post.id)
        self.assertEqual(post.text, TEXT_AFTER_EDIT)
        self.assertEqual(Post.objects.count(), posts_count)
