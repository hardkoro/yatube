from .setup_tests import SetUpTests


class PostModelTest(SetUpTests):
    def test_post_str(self) -> None:
        """Метод __str__ должен вернуть первые 15 символов текста поста."""
        post = PostModelTest.post
        value = PostModelTest.post.text[:15]
        self.assertEqual(value, str(post))

    def test_group_str(self) -> None:
        """Метод __str__ должен вернуть первые название группы."""
        group = PostModelTest.group
        value = PostModelTest.group.title
        self.assertEqual(value, str(group))
