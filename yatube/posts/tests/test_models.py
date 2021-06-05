from .setup_tests import SetUpTests


class ModelRecordsTest(SetUpTests):
    def test_model_str(self):
        """Метод __str__ должен вернуть соответствующие данные."""
        rec_values = {
            self.post: self.post.text[:15],
            self.group: self.group.title,
            self.comment: self.comment.text[:15],
            self.follow: (
                f'{self.follow.user.username} follows '
                f'{self.follow.author.username}'
            )
        }

        for record, value in rec_values.items():
            with self.subTest(record=record):
                self.assertEqual(value, str(record))
