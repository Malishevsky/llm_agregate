#####################################################################################################

import pytest
import pytest_bdd

#####################################################################################################

# pylint: disable=redefined-outer-name,unused-argument

@pytest_bdd.scenario('publish_article.feature', 'Publishing the article')
def test_publish() -> None:
    pass

@pytest_bdd.given("I'm an author user")
def author_user(auth, author) -> None:
    pass

@pytest.fixture()
@pytest_bdd.given('I have an auth')
def auth() -> object:
    return object()

@pytest.fixture()
@pytest_bdd.given('I have an author')
def author() -> object:
    return object()

@pytest.fixture()
@pytest_bdd.given('I have an article')
def article(author) -> object:  # noqa: WPS442
    return object()

@pytest_bdd.when('I go to the article page')
def go_to_article(article) -> None:  # noqa: WPS442
    pass

@pytest_bdd.when('I press the publish button')
def publish_article() -> None:
    pass

@pytest_bdd.then('I should not see the error message')
def no_error_message() -> None:
    pass

@pytest_bdd.then('the article should be published')
def article_is_published(article) -> None:  # noqa: WPS442
    pass

# pylint: enable=redefined-outer-name,unused-argument

#####################################################################################################
