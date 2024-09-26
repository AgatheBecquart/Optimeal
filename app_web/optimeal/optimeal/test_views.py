import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from unittest.mock import patch
from blog.forms import PredictionForm
from authentication.forms import CustomUserChangeForm

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="12345")


@pytest.fixture
def authenticated_client(client, user):
    client.login(username="testuser", password="12345")
    return client


@pytest.mark.django_db
class TestViews:
    def test_home_view(self, client):
        response = client.get(reverse("home"))
        assert response.status_code == 200
        assert "blog/home.html" in [t.name for t in response.templates]

    @patch("blog.views.requests.post")
    def test_predict_view_valid_form(self, mock_post, authenticated_client):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"prediction": 100}

        response = authenticated_client.post(
            reverse("predict_view"), {"id_jour": "2023-05-01"}
        )

        assert response.status_code == 200
        assert "result" in response.context
        assert response.context["result"] == {"prediction": 100}
        assert isinstance(response.context["form"], PredictionForm)

    @patch("blog.views.requests.post")
    def test_predict_view_invalid_form(self, mock_post, authenticated_client):
        response = authenticated_client.post(
            reverse("predict_view"), {"id_jour": "invalid_date"}
        )

        assert response.status_code == 200
        assert "result" not in response.context
        assert isinstance(response.context["form"], PredictionForm)
        assert not response.context["form"].is_valid()

    def test_signup_view(self, client):
        response = client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "testpass123",
                "password2": "testpass123",
                "email": "newuser@example.com",
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("login")
        assert User.objects.filter(username="newuser").exists()

    def test_custom_login_view(self, client):
        response = client.get(reverse("login"))
        assert response.status_code == 200
        assert "authentication/login.html" in [t.name for t in response.templates]

    def test_custom_logout(self, authenticated_client):
        response = authenticated_client.get(reverse("logout"))
        assert response.status_code == 302
        assert response.url == reverse("login")

    def test_profile_update_view(self, authenticated_client):
        response = authenticated_client.get(reverse("profile"))
        assert response.status_code == 200
        assert isinstance(response.context["form"], CustomUserChangeForm)

    def test_user_creation(self, db):
        user = User.objects.create_user(username="testuser2", password="testpass")
        assert User.objects.count() == 1
        assert User.objects.first().username == "testuser2"
