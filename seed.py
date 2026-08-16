# seed.py
# Creates demo accounts and sample data for manually testing search/filter
# and empty-state UI without hand-creating a pile of notes each time.
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

from database import db
from models.user import User
from models.note import Note

DEMO_NOTES = [
    ("Grocery list", "Milk, eggs, spinach, coffee, olive oil.", 2),
    ("Trip planning", "Flights booked. Still need to sort the rental car and pick a hotel near the old town.", 9),
    ("Q3 goals", "Ship the redesign, close out the backlog, start the migration doc.", 5),
    ("Book notes", None, 14),
    ("Recipe idea", "Roast the garlic first, then fold it into the risotto at the end.", 21),
    ("Meeting notes", "Standup: blocked on the API key rotation. Follow up with infra tomorrow.", 1),
    ("Bug repro steps", "1. Log in\n2. Delete last note\n3. Refresh — list still shows it", 3),
    ("Gift ideas", "A good notebook. Maybe the mechanical keyboard.", 18),
    ("Workout plan", "Mon: legs. Wed: push. Fri: pull. Sat: easy run.", 7),
    ("Reading list", "Designing Data-Intensive Applications, ch. 5-7. Then back to the Kafka book.", 12),
    ("Interview prep", "Review system design basics, rehearse the project walkthrough.", 4),
    ("Apartment hunt", None, 25),
    ("Car maintenance", "Oil change due end of month. Check the rear tire pressure again.", 16),
    ("Weekend plans", "Farmers market in the morning, then the trailhead if the weather holds.", 0),
    ("Password vault", "Not actually storing passwords here, just a reminder to set up a real vault.", 28),
]


def _seed_user(username, email, password, status="user"):
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"  {username}: already exists, skipping")
        return existing
    user = User(username=username, email=email, password=generate_password_hash(password))
    user.status = status
    user.email_verified = True
    db.session.add(user)
    db.session.commit()
    print(f"  {username}: created ({status})")
    return user


def seed():
    print("Seeding database...")

    admin = _seed_user("admin", "admin@example.com", "Admin@1234", status="admin")
    demo = _seed_user("demo", "demo@example.com", "Demo@1234")
    _seed_user("empty", "empty@example.com", "Empty@1234")

    if demo and not Note.query.filter_by(user_id=demo.id).first():
        now = datetime.now(timezone.utc)
        for title, content, days_ago in DEMO_NOTES:
            note = Note(title=title, content=content, user_id=demo.id)
            note.created_at = now - timedelta(days=days_ago)
            db.session.add(note)
        db.session.commit()
        print(f"  demo: added {len(DEMO_NOTES)} notes")
    else:
        print("  demo: already has notes, skipping")

    print("Done. Login with admin/Admin@1234, demo/Demo@1234, or empty/Empty@1234.")
