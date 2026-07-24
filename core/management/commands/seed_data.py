import os
import yaml
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Seeds the database with Prem Durbar Hotel & Nagarkot Zipline data from seed_data.yaml. "
        "Supports --update to sync existing records."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="seed_data.yaml",
            help="Path to the seed YAML file (default: seed_data.yaml in project root)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            default=False,
            help="If set, update existing records instead of skipping them.",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        do_update = options["update"]

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Seed file not found: {file_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"Loading seed data from {file_path}..."))

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self.stderr.write(self.style.ERROR(f"Error parsing YAML: {exc}"))
                return

        if not data:
            self.stderr.write(self.style.ERROR("YAML file is empty."))
            return

        # -- 1. Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                "admin", "info@premdurbar.com", "admin123",
                phone="+01-5145351", is_hotel_admin=True, is_guest=False
            )
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' (password: admin123)."))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists. Skipping."))

        # -- 3. Hotel Settings (singleton)
        from settings_manager.models.hotel_settings import HotelSettings
        s = data.get("hotel_settings")
        if s:
            existing = HotelSettings.objects.first()
            if existing:
                for k, v in s.items():
                    setattr(existing, k, v)
                existing.save()
                self.stdout.write(self.style.SUCCESS("Updated Hotel Settings."))
            else:
                HotelSettings.objects.create(**s)
                self.stdout.write(self.style.SUCCESS("Created Hotel Settings."))

        # -- 4. About Preview (singleton)
        from homepage.models.about_preview import AboutPreview
        ap = data.get("about_preview")
        if ap:
            existing = AboutPreview.objects.first()
            if existing:
                for k, v in ap.items():
                    setattr(existing, k, v)
                existing.save()
                self.stdout.write(self.style.SUCCESS("Updated About Preview."))
            else:
                AboutPreview.objects.create(**ap)
                self.stdout.write(self.style.SUCCESS("Created About Preview."))

        # -- 5. Hero Slides
        from homepage.models.hero_slide import HeroSlide
        if do_update:
            HeroSlide.objects.all().delete()
        for slide in data.get("hero_slides", []):
            title = slide.get("title")
            if not title:
                continue
            HeroSlide.objects.get_or_create(
                title=title,
                defaults={k: v for k, v in slide.items() if k != "title"}
            )
            self.stdout.write(self.style.SUCCESS(f"Processed hero slide: {title}"))

        # -- 6. Room Facilities
        from rooms.models.room_facility import RoomFacility
        for fac in data.get("room_facilities", []):
            name = fac.get("name")
            if not name:
                continue
            RoomFacility.objects.get_or_create(
                name=name,
                defaults={k: v for k, v in fac.items() if k != "name"}
            )

        # -- 7. Room Categories
        from rooms.models.room_category import RoomCategory
        for cat in data.get("room_categories", []):
            slug = cat.get("slug")
            if not slug:
                continue
            RoomCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": cat.get("name"),
                    "order": cat.get("order", 0),
                    "is_published": cat.get("is_published", True),
                }
            )

        # -- 8. Rooms
        from rooms.models.room import Room
        if do_update:
            Room.objects.all().delete()
        
        for room_data in data.get("rooms", []):
            slug = room_data.get("slug")
            if not slug:
                continue
            facility_names = room_data.pop("facilities", [])
            images = room_data.pop("images", [])
            policies = room_data.pop("policies", [])
            prices_data = room_data.pop("prices", [])
            
            category_slug = room_data.get("category")
            if category_slug:
                cat_obj = RoomCategory.objects.filter(slug=category_slug).first()
                room_data["category"] = cat_obj

            room_obj, created = Room.objects.get_or_create(
                slug=slug,
                defaults={k: v for k, v in room_data.items()}
            )
            
            from rooms.models.room_base_price import RoomBasePrice
            from settings_manager.models.currency import Currency
            for p_data in prices_data:
                ccode = p_data.get("currency")
                c_obj = Currency.objects.filter(iso_code=ccode).first()
                if c_obj:
                    RoomBasePrice.objects.update_or_create(
                        room=room_obj,
                        currency=c_obj,
                        defaults={
                            'base_price': p_data.get("base_price"),
                            'discount_price': p_data.get("discount_price")
                        }
                    )
            for fname in facility_names:
                fac = RoomFacility.objects.filter(name=fname).first()
                if fac:
                    room_obj.facilities.add(fac)
            
            from rooms.models.room_image import RoomImage
            for img in images:
                RoomImage.objects.get_or_create(
                    room=room_obj,
                    image=img.get("image"),
                    defaults={"is_primary": img.get("is_primary", False), "alt_text": img.get("alt_text", "")}
                )
            
            from rooms.models.room_policy import RoomPolicy
            for pol in policies:
                RoomPolicy.objects.get_or_create(
                    room=room_obj,
                    title=pol.get("title"),
                    defaults={"description": pol.get("description")}
                )

            self.stdout.write(self.style.SUCCESS(f"Processed room: {room_obj.title}"))

        # -- 9. About CMS (singleton)
        from homepage.models.about_cms import AboutCMS
        acms = data.get("about_cms")
        if acms:
            existing = AboutCMS.objects.first()
            if existing:
                if do_update:
                    for k, v in acms.items():
                        setattr(existing, k, v)
                    existing.save()
                    self.stdout.write(self.style.SUCCESS("Updated AboutCMS."))
            else:
                AboutCMS.objects.create(**acms)
                self.stdout.write(self.style.SUCCESS("Created AboutCMS."))

        # -- 9.5. Team Members
        from homepage.models.team_member import TeamMember
        t_members = data.get("team_members", [])
        for tm in t_members:
            TeamMember.objects.update_or_create(
                name=tm["name"],
                defaults={
                    "role": tm.get("role", ""),
                    "bio": tm.get("bio", ""),
                    "order": tm.get("order", 0),
                    "is_published": tm.get("is_published", True),
                }
            )
        if t_members:
            self.stdout.write(self.style.SUCCESS("Seeded Team Members."))

        # -- 10. Zipline CMS (singleton)
        from homepage.models.zipline_cms import ZiplineCMS
        zcms = data.get("zipline_cms")
        if zcms:
            existing = ZiplineCMS.objects.first()
            if existing:
                if do_update:
                    for k, v in zcms.items():
                        setattr(existing, k, v)
                    existing.save()
                    self.stdout.write(self.style.SUCCESS("Updated ZiplineCMS."))
            else:
                ZiplineCMS.objects.create(**zcms)
                self.stdout.write(self.style.SUCCESS("Created ZiplineCMS."))

        # -- 11. Sustainability CMS & Pillars
        from homepage.models.sustainability_cms import SustainabilityCMS, SustainabilityPillar
        scms = data.get("sustainability_cms")
        if scms:
            existing = SustainabilityCMS.objects.first()
            if existing:
                if do_update:
                    for k, v in scms.items():
                        setattr(existing, k, v)
                    existing.save()
                    self.stdout.write(self.style.SUCCESS("Updated SustainabilityCMS."))
            else:
                SustainabilityCMS.objects.create(**scms)
                self.stdout.write(self.style.SUCCESS("Created SustainabilityCMS."))

        if do_update:
            SustainabilityPillar.objects.all().delete()
        for pillar in data.get("sustainability_pillars", []):
            title = pillar.get("title")
            if not title:
                continue
            SustainabilityPillar.objects.get_or_create(
                title=title,
                defaults={k: v for k, v in pillar.items() if k != "title"}
            )

        # -- 12. Testimonials
        from testimonials.models.testimonial import Testimonial
        if do_update:
            Testimonial.objects.all().delete()
        for t in data.get("testimonials", []):
            guest_name = t.get("guest_name")
            source = t.get("source")
            if not guest_name:
                continue
            Testimonial.objects.get_or_create(
                guest_name=guest_name, source=source,
                defaults={k: v for k, v in t.items() if k not in ("guest_name", "source")}
            )

        # -- 13. Branches
        from contact.models.branch import Branch
        if do_update:
            Branch.objects.all().delete()
        for b in data.get("branches", []):
            name = b.get("name")
            if not name:
                continue
            Branch.objects.get_or_create(
                name=name,
                defaults={k: v for k, v in b.items() if k != "name"}
            )

        self.stdout.write(self.style.SUCCESS("\nPrem Durbar database seeding completed successfully!"))
