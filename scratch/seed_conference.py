import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from conference.models.venue import EventVenue  # noqa: E402

venues_data = [
    {
        "name": "Janaki Hall",
        "description": "Step into the grandeur of Janaki Hall at Prem Durbar, a venue that epitomizes elegance and charm. With its opulent decor, facilities, and versatile space, it’s the perfect setting for any prestigious event. Whether hosting a gala, conference, or wedding, Janaki Hall transforms every occasion into a memorable, world-class experience.",
        "capacity": 400,
        "layout_options": "Round Table: 400 pax\nClassroom: 200 pax\nBanquet: 350 pax\nTheatre: 450 pax",
        "base_price": 50000.00,
    },
    {
        "name": "Jyamire Hall",
        "description": "Ascend to the zenith of luxury with Jyamire Hall at Prem Durbar, a beacon of unparalleled sophistication. This majestic hall is a masterpiece, crafted to host the most prestigious international events. With its stunning interiors, state-of-the-art acoustics, and ambient lighting, it creates an atmosphere of exclusivity and grandeur, ensuring every event is nothing short of legendary.",
        "capacity": 150,
        "layout_options": "Classroom: 150 pax\nRound Table: 100 pax\nTheatre: 180 pax\nU-Shape: 80 pax",
        "base_price": 35000.00,
    },
    {
        "name": "Narayani Hall",
        "description": "Narayani Hall at Prem Durbar is where grandeur meets innovation, a prestigious venue that redefines the essence of high-profile events. With its breathtaking design, advanced technological integrations, and impeccable service, it stands as a testament to next-level luxury. Here, every event is transformed into an extraordinary spectacle, setting a new benchmark for elegance and sophistication in the world of hospitality.",
        "capacity": 10,
        "layout_options": "Board Room: 10 pax\nU-Shape: 8 pax\nClassroom: 12 pax",
        "base_price": 15000.00,
    },
    {
        "name": "Balmiki Hall",
        "description": "Balmiki Hall at Prem Durbar is a marvel of architectural beauty and functional elegance, designed to host events that leave a lasting impression. With its luxurious decor, state-of-the-art amenities, and adaptable space, it’s the ideal backdrop for any distinguished gathering. Here, every event is elevated to an art form, ensuring guests experience the pinnacle of refinement and grace.",
        "capacity": 25,
        "layout_options": "U Shape: 25 pax\nClassroom: 30 pax\nBoard Room: 20 pax",
        "base_price": 20000.00,
    }
]

print("Seeding event venues...")
for data in venues_data:
    venue, created = EventVenue.objects.get_or_create(
        name=data["name"],
        defaults={
            "description": data["description"],
            "capacity": data["capacity"],
            "layout_options": data["layout_options"],
            "base_price": data["base_price"],
            "is_active": True,
        }
    )
    if created:
        print(f"Created EventVenue: {venue.name}")
    else:
        print(f"EventVenue already exists: {venue.name}")

print("Seeding complete!")
