import os
import yaml
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.apps import apps

User = get_user_model()

# Global Model Mapping Registry:
# key -> (app_label, model_name, lookup_fields, is_singleton)
GLOBAL_MODEL_REGISTRY = {
    # Settings & Config
    "hotel_settings": ("settings_manager", "HotelSettings", None, True),
    "currencies": ("settings_manager", "Currency", ["iso_code"], False),
    "navigation_menus": ("settings_manager", "NavigationMenu", ["name", "position"], False),
    "seo_banners": ("seo", "SEOData", ["path"], False),
    "payment_processors": ("payments", "PaymentProcessor", ["code"], False),

    # Homepage & CMS
    "about_preview": ("homepage", "AboutPreview", None, True),
    "hero_slides": ("homepage", "HeroSlide", ["title"], False),
    "about_cms": ("homepage", "AboutCMS", None, True),
    "team_members": ("homepage", "TeamMember", ["name"], False),
    "zipline_cms": ("homepage", "ZiplineCMS", None, True),
    "sustainability_cms": ("homepage", "SustainabilityCMS", None, True),
    "sustainability_pillars": ("homepage", "SustainabilityPillar", ["title"], False),

    # Rooms & Facilities
    "room_categories": ("rooms", "RoomCategory", ["slug"], False),
    "room_facilities": ("rooms", "RoomFacility", ["name"], False),

    # Dining
    "dining_categories": ("dining", "DiningCategory", ["slug"], False),

    # Other Apps
    "testimonials": ("testimonials", "Testimonial", ["guest_name", "source"], False),
    "branches": ("contact", "Branch", ["name"], False),
    "contact_inquiry_categories": ("contact", "ContactInquiryCategory", ["slug"], False),
    "coupons": ("booking", "Coupon", ["code"], False),
}


def filter_model_fields(model, data_dict):
    """Dynamically filters dictionary keys to match only real fields present on the target Django model."""
    valid_field_names = {f.name for f in model._meta.get_fields() if not f.is_relation or f.concrete}
    return {k: v for k, v in data_dict.items() if k in valid_field_names}


def prepare_item_data(key, item, valid_data):
    """Applies model-specific dynamic preprocessing (e.g. date calculation for Coupons)."""
    if key == "coupons":
        valid_days = item.get("valid_days_from_now", 365)
        if "valid_from" not in valid_data:
            valid_data["valid_from"] = timezone.now()
        if "valid_to" not in valid_data:
            valid_data["valid_to"] = timezone.now() + timedelta(days=valid_days)
    return valid_data


def post_process_item(key, obj, item):
    """Applies post-creation/update relationship logic (e.g. PaymentProcessor Currency links)."""
    if key == "payment_processors":
        currencies_list = item.get("currencies") or item.get("payment_currencies") or []
        if currencies_list:
            from payments.models.payment_processor import PaymentProcessorCurrency
            from settings_manager.models.currency import Currency
            for ccode in currencies_list:
                # pyrefly: ignore [missing-attribute]
                curr = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=ccode).first()
                if curr:
                    PaymentProcessorCurrency.objects.get_or_create(
                        payment_processor=obj,
                        currency=curr
                    )

    if key == "coupons":
        min_spends_data = item.get("min_spends") or []
        if min_spends_data:
            from booking.models.coupon import CouponMinSpend
            from settings_manager.models.currency import Currency
            for ms in min_spends_data:
                ccode = ms.get("currency")
                min_spend_val = ms.get("min_spend")
                if ccode and min_spend_val is not None:
                    curr = Currency.objects.filter(iso_code=ccode).first()
                    if curr:
                        CouponMinSpend.objects.update_or_create(
                            coupon=obj,
                            currency=curr,
                            defaults={"min_spend": min_spend_val}
                        )


class Command(BaseCommand):
    help = (
        "Single Unified Data Importer for Prem Durbar Hotel & Nagarkot Zipline. "
        "Imports data from YAML files (initial_data.yaml, seed_data.yaml). "
        "If data exists: SKIPS. If --update: UPDATES. If missing: CREATES."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help="Path to specific YAML data file",
        )
        parser.add_argument(
            "--folder",
            type=str,
            default="core/records",
            help="Path to directory containing modular YAML data files (default: core/records)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            default=False,
            help="If set, update existing records instead of skipping them.",
        )

    def handle(self, *args, **options):
        file_path = options.get("file")
        folder_path = options.get("folder")
        do_update = options.get("update", False)

        files_to_process = []
        if file_path:
            files_to_process.append(file_path)
        else:
            if folder_path and os.path.exists(folder_path):
                folder_files = [
                    os.path.join(folder_path, f)
                    for f in sorted(os.listdir(folder_path))
                    if f.endswith(".yaml") or f.endswith(".yml")
                ]
                files_to_process.extend(folder_files)

        # -- 1. Ensure Superuser Admin
        if not User.objects.filter(username="admin").exists():
            # pyrefly: ignore [missing-attribute]
            User.objects.create_superuser(
                "admin", "info@premdurbar.com", "admin123",
                phone="+01-5145351", is_hotel_admin=True, is_guest=False
            )
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' (password: admin123)."))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists. Skipping."))

        for current_file in files_to_process:
            if not os.path.exists(current_file):
                continue

            self.stdout.write(self.style.NOTICE(f"\nProcessing data from {current_file}..."))

            with open(current_file, "r", encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError as exc:
                    self.stderr.write(self.style.ERROR(f"Error parsing YAML ({current_file}): {exc}"))
                    continue

            if not data:
                self.stderr.write(self.style.ERROR(f"YAML file is empty: {current_file}"))
                continue

            # -- 2. Process All Registered Models Dynamically
            for key, config in GLOBAL_MODEL_REGISTRY.items():
                if key not in data:
                    continue

                app_label, model_name, lookup_fields, is_singleton = config
                try:
                    model = apps.get_model(app_label, model_name)
                except LookupError:
                    self.stderr.write(self.style.ERROR(f"Model {app_label}.{model_name} not found."))
                    continue

                raw_data = data[key]

                # SINGLETON MODELS
                if is_singleton:
                    if not isinstance(raw_data, dict):
                        continue
                    valid_data = filter_model_fields(model, raw_data)
                    valid_data = prepare_item_data(key, raw_data, valid_data)

                    existing = model.objects.first()
                    if existing:
                        if do_update:
                            for k, v in valid_data.items():
                                setattr(existing, k, v)
                            existing.save()
                            post_process_item(key, existing, raw_data)
                            self.stdout.write(self.style.SUCCESS(f"  - Updated {model_name} (Singleton)"))
                        else:
                            self.stdout.write(self.style.WARNING(f"  - {model_name} already exists. Skipping."))
                    else:
                        new_obj = model.objects.create(**valid_data)
                        post_process_item(key, new_obj, raw_data)
                        self.stdout.write(self.style.SUCCESS(f"  - Created {model_name} (Singleton)"))

                # COLLECTION MODELS
                else:
                    if not isinstance(raw_data, list):
                        continue

                    count_created = 0
                    count_updated = 0
                    count_skipped = 0

                    for item in raw_data:
                        if not isinstance(item, dict):
                            continue

                        valid_data = filter_model_fields(model, item)
                        valid_data = prepare_item_data(key, item, valid_data)

                        # Special active manager lookup for Currency / PaymentProcessor
                        if model_name == "Currency" and "iso_code" in item:
                            existing = model.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=item["iso_code"]).first()
                        elif model_name == "PaymentProcessor" and "code" in item:
                            existing = model._base_manager.filter(code=item["code"]).first()
                        else:
                            # pyrefly: ignore [not-iterable]
                            lookup_kwargs = {field: item.get(field) for field in lookup_fields if item.get(field) is not None}
                            if not lookup_kwargs:
                                continue
                            existing = model.objects.filter(**lookup_kwargs).first()

                        if existing:
                            if do_update:
                                for k, v in valid_data.items():
                                    setattr(existing, k, v)
                                if hasattr(existing, 'is_active'):
                                    existing.is_active = True
                                if hasattr(existing, 'deleted_at'):
                                    existing.deleted_at = None
                                existing.save()
                                post_process_item(key, existing, item)
                                count_updated += 1
                            else:
                                count_skipped += 1
                        else:
                            new_obj = model.objects.create(**valid_data)
                            post_process_item(key, new_obj, item)
                            count_created += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  - Processed {model_name}: {count_created} created, {count_updated} updated, {count_skipped} skipped."
                        )
                    )

            # -- 3. Complex Models: Rooms with nested FKs, M2Ms, Images, Prices & Policies
            if "rooms" in data:
                from rooms.models.room import Room
                from rooms.models.room_category import RoomCategory
                from rooms.models.room_facility import RoomFacility
                from rooms.models.room_base_price import RoomBasePrice
                from rooms.models.room_image import RoomImage
                from rooms.models.room_policy import RoomPolicy
                from settings_manager.models.currency import Currency

                count_created = 0
                count_updated = 0
                count_skipped = 0

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

                    valid_room_fields = filter_model_fields(Room, room_data)

                    existing = Room.objects.filter(slug=slug).first()
                    if existing:
                        if do_update:
                            for k, v in valid_room_fields.items():
                                setattr(existing, k, v)
                            existing.save()
                            room_obj = existing
                            count_updated += 1
                        else:
                            count_skipped += 1
                            continue
                    else:
                        valid_room_fields["slug"] = slug
                        room_obj = Room.objects.create(**valid_room_fields)
                        count_created += 1

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

                    for img in images:
                        img_path = img.get("image")
                        if img_path:
                            RoomImage.objects.get_or_create(
                                room=room_obj,
                                image=img_path,
                                defaults={"is_primary": img.get("is_primary", False), "alt_text": img.get("alt_text", "")}
                            )

                    for pol in policies:
                        RoomPolicy.objects.get_or_create(
                            room=room_obj,
                            title=pol.get("title"),
                            defaults={"description": pol.get("description")}
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  - Processed Room: {count_created} created, {count_updated} updated, {count_skipped} skipped."
                    )
                )

            # -- 4. Dining Items with Category FK & Multi-Currency Base Prices
            if "dining_items" in data:
                from dining.models.item import DiningItem, DiningCategory, DiningItemBasePrice
                from settings_manager.models.currency import Currency
                from django.utils.text import slugify

                count_created = 0
                count_updated = 0
                count_skipped = 0

                for item_data in data.get("dining_items", []):
                    cat_identifier = item_data.pop("category", None)
                    cat_obj = None
                    if cat_identifier:
                        cat_obj = DiningCategory.objects.filter(slug=cat_identifier).first() or DiningCategory.objects.filter(name=cat_identifier).first()

                    if not cat_obj:
                        continue

                    prices_data = item_data.pop("prices", [])
                    title = item_data.get("title")
                    if not title:
                        continue

                    slug = item_data.get("slug") or slugify(title)
                    valid_fields = filter_model_fields(DiningItem, item_data)
                    valid_fields["category"] = cat_obj

                    existing = DiningItem.objects.filter(slug=slug).first()
                    if existing:
                        if do_update:
                            for k, v in valid_fields.items():
                                setattr(existing, k, v)
                            existing.save()
                            item_obj = existing
                            count_updated += 1
                        else:
                            count_skipped += 1
                            continue
                    else:
                        valid_fields["slug"] = slug
                        item_obj = DiningItem.objects.create(**valid_fields)
                        count_created += 1

                    for p_data in prices_data:
                        ccode = p_data.get("currency")
                        c_obj = Currency.objects.filter(iso_code=ccode).first()
                        if c_obj:
                            DiningItemBasePrice.objects.update_or_create(
                                item=item_obj,
                                currency=c_obj,
                                defaults={'base_price': p_data.get("base_price")}
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  - Processed DiningItem: {count_created} created, {count_updated} updated, {count_skipped} skipped."
                    )
                )

            # -- 5. Zipline Packages with Multi-Currency Base Prices
            if "zipline_packages" in data:
                from homepage.models.zipline_package import ZiplinePackage, ZiplinePackageBasePrice
                from settings_manager.models.currency import Currency
                from django.utils.text import slugify

                count_created = 0
                count_updated = 0
                count_skipped = 0

                for item_data in data.get("zipline_packages", []):
                    prices_data = item_data.pop("prices", [])
                    name = item_data.get("name")
                    if not name:
                        continue

                    slug = item_data.get("slug") or slugify(name)
                    valid_fields = filter_model_fields(ZiplinePackage, item_data)

                    existing = ZiplinePackage.objects.filter(slug=slug).first()
                    if existing:
                        if do_update:
                            for k, v in valid_fields.items():
                                setattr(existing, k, v)
                            existing.save()
                            pkg_obj = existing
                            count_updated += 1
                        else:
                            count_skipped += 1
                            continue
                    else:
                        valid_fields["slug"] = slug
                        pkg_obj = ZiplinePackage.objects.create(**valid_fields)
                        count_created += 1

                    for p_data in prices_data:
                        ccode = p_data.get("currency")
                        c_obj = Currency.objects.filter(iso_code=ccode).first()
                        if c_obj:
                            ZiplinePackageBasePrice.objects.update_or_create(
                                package=pkg_obj,
                                currency=c_obj,
                                defaults={
                                    'base_price': p_data.get("base_price"),
                                    'discount_price': p_data.get("discount_price")
                                }
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  - Processed ZiplinePackage: {count_created} created, {count_updated} updated, {count_skipped} skipped."
                    )
                )

        self.stdout.write(self.style.SUCCESS("\nAll data import tasks completed successfully!"))
