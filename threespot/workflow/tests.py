from datetime import date, timedelta
from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django import forms
from django.test import TestCase

from threespot.workflow.admin import WorkflowAdmin
from threespot.workflow.app_settings import PUBLISHED_STATE
from threespot.workflow.forms import WorkflowAdminFormMixin
from threespot.workflow.models import WorkflowMixin


class TestArticle(WorkflowMixin, models.Model):
    """A mock object for testing workflow"""
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.title


class TestDatedArticle(WorkflowMixin, models.Model):
    """A mock object for testing workflow"""
    pubdate = models.DateField()
    slug = models.SlugField()
    title = models.CharField(max_length=255)

    class Meta:
        get_latest_by = 'pubdate'

    def __unicode__(self):
        return self.title


class TestArticleAdminForm(WorkflowAdminFormMixin):
    
    class Meta:
        model = TestArticle

class TestArticleAdmin(WorkflowAdmin):
    form = TestArticleAdminForm

admin.site.register(TestArticle, TestArticleAdmin)

class WorkflowTest(TestCase):

    csrf_disabled = False
    test_user = 'testrunner'
    test_password = 'testrunner'

    def _disable_csrf_middleware(self):
        settings.MIDDLEWARE_CLASSES = filter(lambda m: 'CsrfMiddleware' \
            not in m, settings.MIDDLEWARE_CLASSES
        )
        self.csrf_disabled = True

    def _setup_admin(self):
        """
        Check to see if test runner user was already created (perhaps by 
        another test case) and if not, create it.
        """
        try:
            User.objects.get(username=self.test_user)
        except User.DoesNotExist:
            user = User.objects.create_superuser(
                self.test_user,
                'test@localhost.com',
                self.test_password
            )
            user.save()
        # Install admin:
        admin_patterns = patterns(
            (r'^admin/', include(admin.site.urls)),
        )
        from urls import urlpatterns
        urlpatterns = admin_patterns + urlpatterns

    def _log_test_client_in(self, login_url=None):
        """Log the test client in using the test runner user"""
        self._setup_admin()
        if not login_url:
            from django.conf.global_settings import LOGIN_URL as login_url
        return self.client.login(
            username=self.test_user,
            password=self.test_password
        )
    
    def _log_test_client_out(self):
        """Log the test client out using the test runner user"""
        self.client.logout()
    
    def _get_admin_urls(self, obj):
        opts = TestArticle._meta
        urls = {}
        arg = hasattr(obj, 'pk') and obj.pk or obj
        prefix = "admin:%s_%s_" % (opts.app_label, opts.module_name)
        urls['add'] = reverse(prefix + "add")
        urls['index'] = reverse(prefix + 'changelist')
        for view in ('change','delete', 'copy', 'merge'):
            urls[view] = reverse(prefix + view, args=(arg,))
        return urls
    
    def get_admin_url(self, name, obj):
        urls = self._get_admin_urls(obj)
        return urls.get(name)
    
    def login(self):
        """Log client in."""
        if not self.csrf_disabled:
            self._disable_csrf_middleware()
        self._log_test_client_in()
    
    def test_status(self):
        """ Verify that workflow status works as expected."""
        article = TestArticle(
            slug = 'article',
            title = 'Title',
            status = PUBLISHED_STATE
        )
        article.save()
        self.assertTrue(article.is_published())
        self.assertTrue(
            article.pk in [a.pk for a in TestArticle.objects.published()]
        )
        article.unpublish()
        self.assertTrue(not article.is_published())
        self.assertTrue(
            article.pk in [a.pk for a in TestArticle.objects.unpublished()]
        )
        article.publish()
        self.assertTrue(article.is_published())
    
    def test_postdated_publishing(self):
        """
        Verify that workflow status with postdated publishing works as
        expected.
        """
        from threespot.workflow import app_settings
        app_settings.ENABLE_POSTDATED_PUBLISHING = True
        
        article = TestDatedArticle(
            slug = 'article',
            title = 'Title',
            pubdate = date.today() + timedelta(days=1),
            status = PUBLISHED_STATE
        )
        article.save()
        self.assertFalse(article.is_published())
        self.assertTrue(
            article.pk not in [a.pk for a in \
                TestDatedArticle.objects.published()
            ]
        )
        article.pubdate = date.today()
        article.save()
        self.assertTrue(article.is_published())
        self.assertTrue(
            article.pk in [a.pk for a in TestDatedArticle.objects.published()]
        )
    
    def test_draft_copy_and_merge(self):
        """ Test that draft copy mode works as expected."""
        article = TestArticle(
            slug = 'article',
            title = 'Title',
            status = PUBLISHED_STATE
        )
        article.save()
        self.login()
        # Test draft copying.
        articles = TestArticle.objects.all()
        response = self.client.get(self.get_admin_url('copy', article))
        self.assertTrue(not response.context['draft_already_exists'])
        self.assertEqual(response.context['object'].pk, article.pk)
        response = self.client.post(
            self.get_admin_url('copy', article),
            {'id': article.pk}
        )
        self.assertTrue(len(TestArticle.objects.all()) == 2)
        self.assertTrue(len(TestArticle.objects.published()) == 1)
        self.assertTrue(len(TestArticle.objects.unpublished()) == 1)
        self.assertTrue(len(TestArticle.objects.draft_copies()) == 1)
        draft_article = TestArticle.objects.draft_copies()[0]
        self.assertEqual(draft_article.slug, article.slug + "-draft-copy")
        # Verify that you can't create a second draft copy.
        response = self.client.get(self.get_admin_url('copy', article))
        self.assertTrue(response.context['draft_already_exists'])
        response = self.client.post(
            self.get_admin_url('copy', article),
            {'id': article.pk}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response._headers['location'][1].endswith("/copy/"))
        # Verify that you can't create a draft of a draft.
        response = self.client.post(
            self.get_admin_url('copy', draft_article),
            {'id': article.pk}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response._headers['location'][1].endswith("/copy/"))
        # Test draft merging.
        draft_article.title = "A new title"
        draft_article.save()
        response = self.client.get(self.get_admin_url('merge', draft_article))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            self.get_admin_url('merge', draft_article),
            {'id': article.pk}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response._headers['location'][1].endswith(
            self.get_admin_url('index', article)
        ))
        self.assertEqual(
            TestArticle.objects.get(slug="article").title,
            "A new title"
        )
        self.assertTrue(len(TestArticle.objects.all()) == 1)

    def test_admin_form(self):
        """ Verify the form prevents us from publishing a draft copy."""
        article = TestArticle(
            slug = 'article',
            title = 'Title',
            status = PUBLISHED_STATE
        )
        article.save()
        self.login()
        response = self.client.post(
            self.get_admin_url('copy', article),
            {'id': article.pk}
        )
        draft_article = TestArticle.objects.draft_copies()[0]
        
        response = self.client.post(
            self.get_admin_url('change', draft_article),
            {
                'id': article.pk,
                'title': 'Title',
                'status': PUBLISHED_STATE
            }
        )
        expected_err_string = (
            "This test article is a copy of a draft test article that is "
            "already published. If you want to publish this over top of the "
            "existing item, you can do so by merging it."
        )
        self.assertTrue(expected_err_string in response.context['errors'][1])