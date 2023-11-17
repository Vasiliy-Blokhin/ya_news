from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор', id=1)


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель', id=2)


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        id=1,
    )
    return news


@pytest.fixture
def create_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def id_for_args_n(news):
    return news.id,


@pytest.fixture
def first_text_for_comment():
    return 'Текст заметки'


@pytest.fixture
def comment(author, news, first_text_for_comment):
    comment = Comment.objects.create(
        text=first_text_for_comment,
        id=1,
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def create_comments(author, news):
    Comment.objects.all().delete()
    now = timezone.now()
    all_comments = [
        Comment(
            text=f'Tекст {index}',
            created=now + timedelta(days=index),
            news=news,
            author=author
        )
        for index in range(2)
    ]
    Comment.objects.bulk_create(all_comments)


@pytest.fixture
def id_for_args_c(comment):
    return comment.id,


@pytest.fixture
def comment_data():
    return {
        'text': 'test text'
    }
