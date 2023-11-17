from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    comment_data,
    id_for_args_n
):
    url = reverse('news:detail', args=id_for_args_n)
    client.post(url, data=comment_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    author_client,
    comment_data,
    id_for_args_n,
    news,
    author
):
    url = reverse('news:detail', args=id_for_args_n)
    response = author_client.post(url, data=comment_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, id_for_args_n):
    url = reverse('news:detail', args=id_for_args_n)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client,
    id_for_args_c,
    id_for_args_n
):
    url = reverse('news:delete', args=id_for_args_c)
    response = author_client.delete(url)
    news_url = reverse('news:detail', args=id_for_args_n)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_other_user_cant_delete_comment(
    reader_client,
    id_for_args_c,
):
    url = reverse('news:delete', args=id_for_args_c)
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client,
    id_for_args_c,
    id_for_args_n,
    comment_data,
    comment
):
    url = reverse('news:edit', args=id_for_args_c)
    response = author_client.post(url, data=comment_data)
    news_url = reverse('news:detail', args=id_for_args_n) + '#comments'
    assertRedirects(response, news_url)
    comment.refresh_from_db()
    assert comment.text == comment_data['text']


def test_user_cant_edit_comment_of_another_user(
    reader_client,
    id_for_args_c,
    comment_data, comment,
    first_text_for_comment
):
    url = reverse('news:edit', args=id_for_args_c)
    response = reader_client.post(url, data=comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == first_text_for_comment
