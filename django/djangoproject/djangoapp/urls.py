from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public story browsing
    path("", views.story_list, name="story_list"),
    path("story/<int:story_id>/start/", views.start_story, name="start_story"),
    path("page/<int:page_id>/<int:story_id>/", views.show_page, name="show_page"),
    # Story statistics
    path("statistics/", views.statistics, name="statistics"),
    # Author views (require login)
    path("my-stories/", views.my_stories, name="my_stories"),
    path("story/create/", views.create_story, name="create_story"),
    path("story/<int:story_id>/edit/", views.edit_story, name="edit_story"),
    path("story/<int:story_id>/delete/", views.delete_story, name="delete_story"),
    # Author publish/unpublish their own stories
    path(
        "story/<int:story_id>/publish/",
        views.publish_story_author,
        name="publish_story_author",
    ),
    path(
        "story/<int:story_id>/unpublish/",
        views.unpublish_story_author,
        name="unpublish_story_author",
    ),
    # Ratings and reports (require login)
    path("story/<int:story_id>/rate/", views.rate_story, name="rate_story"),
    path("story/<int:story_id>/report/", views.report_story, name="report_story"),
    # CHANGED: moderation instead of admin to avoid conflict with Django admin
    path("moderation/reports/", views.admin_reports, name="admin_reports"),
    path(
        "moderation/report/<int:report_id>/resolve/",
        views.resolve_report,
        name="resolve_report",
    ),
    path(
        "moderation/story/<int:story_id>/suspend/",
        views.suspend_story,
        name="suspend_story",
    ),
    path(
        "moderation/story/<int:story_id>/publish/",
        views.publish_story,
        name="publish_story",
    ),
    # Authentication
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="djangoapp/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
