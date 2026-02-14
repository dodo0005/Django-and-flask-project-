from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Count, Avg
from django.contrib import messages
from .models import Play, Rating, Report
from .services import flask_api
import requests


# ------------------------
# PUBLIC / READER VIEWS
# ------------------------


def story_list(request):
    """List all published stories from Flask API"""
    try:
        stories = flask_api.get_published_stories()

        # Enhance with Django data (ratings, play counts)
        for story in stories:
            story_id = story["id"]
            # Get average rating
            ratings = Rating.objects.filter(story_id=story_id)
            if ratings.exists():
                story["avg_rating"] = ratings.aggregate(Avg("rating"))["rating__avg"]
                story["rating_count"] = ratings.count()
            else:
                story["avg_rating"] = None
                story["rating_count"] = 0

            # Get play count
            story["play_count"] = Play.objects.filter(story_id=story_id).count()

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Could not fetch stories from Flask API: {e}", status=500)

    return render(request, "djangoapp/story_list.html", {"stories": stories})


def start_story(request, story_id):
    """Start playing a story - get start page and redirect"""
    try:
        start_info = flask_api.get_start_page(story_id)
    except requests.exceptions.RequestException:
        return HttpResponse("Could not get start page from Flask API", status=500)

    start_page_id = start_info.get("start_page_id")
    if not start_page_id:
        messages.error(request, "This story has no start page set.")
        return redirect("story_list")

    return redirect("show_page", page_id=start_page_id, story_id=story_id)


def show_page(request, page_id, story_id):
    """Display a page with choices"""
    try:
        page = flask_api.get_page(page_id)
    except requests.exceptions.RequestException:
        return HttpResponse("Could not fetch page from Flask API", status=500)

    # If ending → save play
    if page.get("is_ending"):
        Play.objects.create(
            story_id=story_id,
            ending_page_id=page_id,
            user=request.user if request.user.is_authenticated else None,
        )

    # Choices come from Flask
    choices = page.get("choices", [])

    return render(
        request,
        "djangoapp/page.html",
        {"page": page, "choices": choices, "story_id": story_id},
    )


# ------------------------
# AUTHOR VIEWS
# ------------------------


@login_required
def my_stories(request):
    """Show stories created by the current user"""
    try:
        all_stories = flask_api.get_stories_by_author(request.user.id)
    except requests.exceptions.RequestException:
        return HttpResponse("Could not fetch stories", status=500)

    return render(request, "djangoapp/my_stories.html", {"stories": all_stories})


@login_required
def create_story(request):
    """Create a new story with story builder interface"""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        # Get pages and choices data
        pages_data = request.POST.getlist("page_text[]")
        pages_ending = request.POST.getlist("page_ending[]")
        pages_ending_label = request.POST.getlist("page_ending_label[]")

        try:
            # 1. Create story in Flask
            publish_immediately = request.POST.get("publish_immediately") == "true"
            status = "published" if publish_immediately else "draft"
            result = flask_api.create_story(
                title, description, status=status, author_id=request.user.id
            )
            story_id = result["id"]

            # 2. Create pages
            page_ids = []
            for i, page_text in enumerate(pages_data):
                is_ending = str(i) in pages_ending
                ending_label = (
                    pages_ending_label[i] if i < len(pages_ending_label) else None
                )
                is_start = i == 0  # First page is start page

                page_result = flask_api.create_page(
                    story_id,
                    text=page_text,
                    is_ending=is_ending,
                    ending_label=ending_label if is_ending else None,
                    is_start_page=is_start,
                )
                page_ids.append(page_result["id"])

            # 3. Create choices
            for i, page_id in enumerate(page_ids):
                # Get choices for this page from form data
                choice_prefix = f"choice_{i}_"
                choice_texts = request.POST.getlist(f"{choice_prefix}text[]")
                choice_targets = request.POST.getlist(f"{choice_prefix}target[]")

                for text, target in zip(choice_texts, choice_targets):
                    if text and target:  # Only create if both are filled
                        target_idx = int(target)
                        if target_idx < len(page_ids):
                            flask_api.create_choice(
                                page_id, text=text, next_page_id=page_ids[target_idx]
                            )

            messages.success(request, f"Story '{title}' created successfully!")
            return redirect("story_list")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error creating story: {e}")
            return redirect("create_story")

    return render(request, "djangoapp/create_story.html")


@login_required
def edit_story(request, story_id):
    """Edit a story and its pages/choices via Flask API"""
    try:
        story = flask_api.get_story(story_id)
        pages = flask_api.get_story_pages(story_id)
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Could not fetch story from Flask API: {e}", status=500)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        status = request.POST.get("status")

        try:
            # 1. Update story metadata
            flask_api.update_story(
                story_id,
                title=title,
                description=description,
                status=status,
                requesting_author_id=request.user.id,
            )

            # 2. Update existing pages
            existing_page_ids = request.POST.getlist("existing_page_id[]")
            existing_page_texts = request.POST.getlist("existing_page_text[]")
            existing_is_ending = request.POST.getlist("existing_page_ending[]")
            existing_ending_labels = request.POST.getlist(
                "existing_page_ending_label[]"
            )

            for i, page_id in enumerate(existing_page_ids):
                is_ending = page_id in existing_is_ending
                flask_api.update_page(
                    int(page_id),
                    text=existing_page_texts[i] if i < len(existing_page_texts) else "",
                    is_ending=is_ending,
                    ending_label=(
                        existing_ending_labels[i]
                        if i < len(existing_ending_labels)
                        else None
                    ),
                )

            # 3. Delete removed pages
            pages_to_delete = request.POST.getlist("delete_page[]")
            for page_id in pages_to_delete:
                flask_api.delete_page(int(page_id))

            # 4. Handle choices for existing pages
            for page_id in existing_page_ids:
                if page_id in pages_to_delete:
                    continue

                # Delete removed choices
                choices_to_delete = request.POST.getlist(f"delete_choice_{page_id}[]")
                for choice_id in choices_to_delete:
                    flask_api.delete_choice(int(page_id), int(choice_id))

                # Update existing choices
                choice_ids = request.POST.getlist(f"choice_id_{page_id}[]")
                choice_texts = request.POST.getlist(f"choice_text_{page_id}[]")
                choice_targets = request.POST.getlist(f"choice_target_{page_id}[]")

                for j, choice_id in enumerate(choice_ids):
                    if choice_id in choices_to_delete:
                        continue
                    if (
                        j < len(choice_texts)
                        and j < len(choice_targets)
                        and choice_texts[j]
                        and choice_targets[j]
                    ):
                        flask_api.update_choice(
                            int(page_id),
                            int(choice_id),
                            text=choice_texts[j],
                            next_page_id=int(choice_targets[j]),
                        )

                # Add new choices for existing pages
                new_choice_texts = request.POST.getlist(f"new_choice_text_{page_id}[]")
                new_choice_targets = request.POST.getlist(
                    f"new_choice_target_{page_id}[]"
                )
                for text, target in zip(new_choice_texts, new_choice_targets):
                    if text and target:
                        flask_api.create_choice(
                            int(page_id), text=text, next_page_id=int(target)
                        )

            # 5. Add new pages
            new_page_texts = request.POST.getlist("new_page_text[]")
            new_page_endings = request.POST.getlist("new_page_ending[]")
            new_page_labels = request.POST.getlist("new_page_ending_label[]")

            new_page_ids = []
            for i, text in enumerate(new_page_texts):
                if not text.strip():
                    new_page_ids.append(None)
                    continue
                is_ending = str(i) in new_page_endings
                label = new_page_labels[i] if i < len(new_page_labels) else None
                result = flask_api.create_page(
                    story_id,
                    text=text,
                    is_ending=is_ending,
                    ending_label=label if is_ending else None,
                )
                new_page_ids.append(result["id"])

            # 6. Add choices for new pages
            for i, new_pid in enumerate(new_page_ids):
                if new_pid is None:
                    continue
                new_choice_texts = request.POST.getlist(f"new_page_choice_text_{i}[]")
                new_choice_targets = request.POST.getlist(
                    f"new_page_choice_target_{i}[]"
                )
                for text, target in zip(new_choice_texts, new_choice_targets):
                    if text and target:
                        flask_api.create_choice(
                            new_pid, text=text, next_page_id=int(target)
                        )

            messages.success(request, "Story updated successfully!")
            return redirect("my_stories")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error updating story: {e}")

    # Build a flat list of all page IDs for the "goes to" dropdowns
    all_page_ids = [p["id"] for p in pages]

    return render(
        request,
        "djangoapp/story_form.html",
        {
            "story": story,
            "pages": pages,
            "all_page_ids": all_page_ids,
        },
    )


@login_required
def delete_story(request, story_id):
    """Delete a story via Flask API"""
    try:
        story = flask_api.get_story(story_id)
    except requests.exceptions.RequestException:
        return HttpResponse("Could not fetch story", status=500)

    if request.method == "POST":
        try:
            flask_api.delete_story(story_id, requesting_author_id=request.user.id)
            messages.success(request, "Story deleted successfully!")
            return redirect("story_list")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error deleting story: {e}")

    return render(request, "djangoapp/confirm_delete.html", {"story": story})


# ------------------------
# STATISTICS
# ------------------------


def statistics(request):
    """Show statistics about plays and endings"""
    # Group plays by story
    play_stats = (
        Play.objects.values("story_id")
        .annotate(total_plays=Count("id"))
        .order_by("-total_plays")
    )

    # Get ending distribution for each story
    ending_stats = Play.objects.values("story_id", "ending_page_id").annotate(
        count=Count("id")
    )

    return render(
        request,
        "djangoapp/statistics.html",
        {
            "play_stats": play_stats,
            "ending_stats": ending_stats,
        },
    )


# ------------------------
# LEVEL 18: RATINGS & COMMENTS
# ------------------------


@login_required
def rate_story(request, story_id):
    """Rate and comment on a story"""
    if request.method == "POST":
        rating_value = request.POST.get("rating")
        comment = request.POST.get("comment", "")

        # Update or create rating
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            story_id=story_id,
            defaults={"rating": rating_value, "comment": comment},
        )

        messages.success(request, "Your rating has been saved!")
        return redirect("story_list")

    # Get existing rating if any
    try:
        existing_rating = Rating.objects.get(user=request.user, story_id=story_id)
    except Rating.DoesNotExist:
        existing_rating = None

    try:
        story = flask_api.get_story(story_id)
    except requests.exceptions.RequestException:
        return HttpResponse("Could not fetch story", status=500)

    return render(
        request,
        "djangoapp/rate_story.html",
        {"story": story, "existing_rating": existing_rating},
    )


@login_required
def report_story(request, story_id):
    """Report a story for moderation"""
    if request.method == "POST":
        reason = request.POST.get("reason")
        description = request.POST.get("description", "")

        Report.objects.create(
            user=request.user, story_id=story_id, reason=reason, description=description
        )

        messages.success(request, "Report submitted. Thank you!")
        return redirect("story_list")

    try:
        story = flask_api.get_story(story_id)
    except requests.exceptions.RequestException:
        return HttpResponse("Could not fetch story", status=500)

    return render(request, "djangoapp/report_story.html", {"story": story})


# ------------------------
# ADMIN / MODERATION
# ------------------------


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reports(request):
    """View all reports (admin only)"""
    reports = Report.objects.filter(resolved=False).order_by("-created_at")
    return render(request, "djangoapp/admin_reports.html", {"reports": reports})


@login_required
@user_passes_test(lambda u: u.is_staff)
def resolve_report(request, report_id):
    """Mark a report as resolved"""
    report = get_object_or_404(Report, id=report_id)
    report.resolved = True
    report.save()
    messages.success(request, "Report marked as resolved.")
    return redirect("admin_reports")


@login_required
@user_passes_test(lambda u: u.is_staff)
def suspend_story(request, story_id):
    """Suspend a story (admin only)"""
    try:
        flask_api.update_story(story_id, status="suspended")
        messages.success(request, "Story suspended.")
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error suspending story: {e}")

    return redirect("story_list")


@login_required
@user_passes_test(lambda u: u.is_staff)
def publish_story(request, story_id):
    """Publish a story (admin only)"""
    try:
        flask_api.update_story(story_id, status="published")
        messages.success(request, "Story published.")
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error publishing story: {e}")

    return redirect("story_list")


# ------------------------
# USER REGISTRATION
# ------------------------


def register(request):
    """User registration"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f"Welcome {user.username}! Your account has been created."
            )
            return redirect("story_list")
    else:
        form = UserCreationForm()

    return render(request, "djangoapp/register.html", {"form": form})


@login_required
def publish_story_author(request, story_id):
    """Author publishes their own story (draft → published)"""
    if request.method == "POST":
        try:
            flask_api.update_story(story_id, status="published")
            messages.success(
                request, "✅ Story published! It's now visible to everyone."
            )
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error publishing story: {e}")

    return redirect("my_stories")


@login_required
def unpublish_story_author(request, story_id):
    """Author unpublishes their story (published → draft)"""
    if request.method == "POST":
        try:
            flask_api.update_story(story_id, status="draft")
            messages.success(
                request, "📥 Story unpublished. It's now only visible to you."
            )
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error unpublishing story: {e}")

    return redirect("my_stories")
