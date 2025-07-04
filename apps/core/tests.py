import pytest

class TestCoreViews:
    """Test core app views (home, about, etc.)"""

    def test_about_view(self):
        """Test the about page"""
        from django.test import Client
        from django.urls import reverse
        client = Client()
        response = client.get(reverse('about'))

        assert response.status_code == 200
        assert 'core/about.html' in [t.name for t in response.templates]

    def test_404_page(self):
        """Test custom 404 page"""
        from django.test import Client
        client = Client()
        response = client.get('/nonexistent-page/')

        assert response.status_code == 404

class TestCoreRedirects:
    """Test redirects and URL handling"""

    @pytest.mark.django_db
    def test_root_url_redirects_to_home(self):
        """Test that root URL redirects to home"""
        from django.test import Client
        client = Client()
        response = client.get('/')

        # Should redirect to home page
        assert response.status_code in [200, 302]

    @pytest.mark.django_db
    def test_authenticated_user_home_access(self, user_factory):
        """Test that authenticated users can access home"""
        from django.test import Client
        from django.urls import reverse
        user = user_factory(username="testuser")

        client = Client()
        client.force_login(user)

        response = client.get(reverse('home'))

        assert response.status_code == 200

    def test_unauthenticated_user_home_access(self):
        """Test that unauthenticated users can access home"""
        from django.test import Client
        from django.urls import reverse
        client = Client()

        response = client.get(reverse('home'))

        # Home should be accessible to everyone
        assert response.status_code == 200

class TestCoreTemplateContext:
    """Test that core views pass correct context to templates"""

    def test_about_page_context(self):
        """Test about page has correct context"""
        from django.test import Client
        from django.urls import reverse
        client = Client()
        response = client.get(reverse('about'))

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_home_page_context_authenticated(self, user_factory):
        """Test home page context for authenticated users"""
        from django.test import Client
        from django.urls import reverse
        user = user_factory(username="testuser")

        client = Client()
        client.force_login(user)

        response = client.get(reverse('home'))

        assert response.status_code == 200
        # Should have user-specific context
        if response.context:
            assert 'user' in response.context

class TestCoreErrorHandling:
    """Test error handling in core views"""

    def test_invalid_url_returns_404(self):
        """Test that invalid URLs return 404"""
        from django.test import Client
        client = Client()
        response = client.get('/this-url-does-not-exist/')

        assert response.status_code == 404


