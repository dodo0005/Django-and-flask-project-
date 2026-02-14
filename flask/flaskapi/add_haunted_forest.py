# add_haunted_forest.py
from extensions import db
from models import Story, Page, Choice

# --- IMPORT OR CREATE YOUR FLASK APP ---
# If your Flask app is directly in app.py:
from app import app  # replace 'app' with your Flask app variable if different

# If you use a factory:
# from app import create_app
# app = create_app()

# --- WRAP ALL DB OPERATIONS IN APP CONTEXT ---
with app.app_context():
    # --- 1. Create the story ---
    story = Story(
        title="The Haunted Forest",
        description="A spooky adventure where you explore a mysterious forest and make choices that determine your fate.",
        status="published",
    )
    db.session.add(story)
    db.session.commit()  # so story.id is available

    # --- 2. Create pages ---
    p1 = Page(
        story_id=story.id,
        text="You wake up at the edge of a dark, haunted forest. Two paths lie before you: a foggy trail to the left and a shadowy path to the right.",
    )
    p2 = Page(
        story_id=story.id,
        text="You walk along the foggy trail and find a glowing lantern on the ground.",
    )
    p3 = Page(
        story_id=story.id,
        text="The shadowy path leads you to a creepy cabin with a faint light inside.",
    )
    p4 = Page(
        story_id=story.id,
        text="The lantern lights your way and you discover a hidden treasure chest!",
    )
    p5 = Page(
        story_id=story.id,
        text="You continue walking in the fog and fall into a trap set by forest spirits.",
        is_ending=True,
        ending_label="Caught by forest spirits",
    )
    p6 = Page(story_id=story.id, text="Inside the cabin, you see a mysterious figure.")
    p7 = Page(
        story_id=story.id,
        text="You run back into the forest but get lost forever.",
        is_ending=True,
        ending_label="Lost in the forest",
    )
    p8 = Page(
        story_id=story.id,
        text="The chest contains magical artifacts that protect you forever.",
        is_ending=True,
        ending_label="Treasure found",
    )
    p9 = Page(
        story_id=story.id,
        text="You move on but trip over a root and injure yourself.",
        is_ending=True,
        ending_label="Injured and lost",
    )
    p10 = Page(
        story_id=story.id,
        text="The figure gives you a map to safely leave the forest.",
        is_ending=True,
        ending_label="Guided to safety",
    )
    p11 = Page(
        story_id=story.id,
        text="You hide until dawn, and the figure disappears.",
        is_ending=True,
        ending_label="Survived but scared",
    )

    db.session.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11])
    db.session.commit()

    # --- 3. Add choices ---
    # Page 1 choices
    c1 = Choice(page_id=p1.id, text="Take the left path", next_page_id=p2.id)
    c2 = Choice(page_id=p1.id, text="Take the right path", next_page_id=p3.id)

    # Page 2 choices
    c3 = Choice(page_id=p2.id, text="Pick up the lantern", next_page_id=p4.id)
    c4 = Choice(page_id=p2.id, text="Leave it and continue", next_page_id=p5.id)

    # Page 3 choices
    c5 = Choice(page_id=p3.id, text="Enter the cabin", next_page_id=p6.id)
    c6 = Choice(page_id=p3.id, text="Run away", next_page_id=p7.id)

    # Page 4 choices
    c7 = Choice(page_id=p4.id, text="Open the chest", next_page_id=p8.id)
    c8 = Choice(page_id=p4.id, text="Ignore it and move on", next_page_id=p9.id)

    # Page 6 choices
    c9 = Choice(page_id=p6.id, text="Talk to the figure", next_page_id=p10.id)
    c10 = Choice(page_id=p6.id, text="Hide", next_page_id=p11.id)

    db.session.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
    db.session.commit()

    # --- 4. Set story start page ---
    story.start_page_id = p1.id
    db.session.commit()

    print("Haunted Forest story added successfully!")
