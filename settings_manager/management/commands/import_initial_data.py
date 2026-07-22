import os
import yaml
from django.core.management.base import BaseCommand
from settings_manager.models.hotel_settings import HotelSettings
from settings_manager.models.currency import Currency
from settings_manager.models.navigation import NavigationMenu
from seo.models.seo_data import SEOData


class Command(BaseCommand):
    help = "Safely imports initial hotel configuration, currencies, and navigation links from a YAML file. Skips items that already exist — never deletes data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="initial_data.yaml",
            help="Path to the YAML data file (default: initial_data.yaml in project root)",
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
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"Loading data from {file_path}..."))

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self.stderr.write(self.style.ERROR(f"Error parsing YAML: {exc}"))
                return

        if not data:
            self.stderr.write(self.style.ERROR("YAML file is empty."))
            return

        # 1. Import / Update Hotel Settings (singleton)
        settings_data = data.get("hotel_settings")
        if settings_data:
            existing = HotelSettings.objects.first()
            if existing and not do_update:
                self.stdout.write(self.style.WARNING(
                    "Hotel Global Settings already exist. Use --update to overwrite. Skipping."
                ))
            elif existing and do_update:
                for field, value in settings_data.items():
                    setattr(existing, field, value)
                existing.save()
                self.stdout.write(self.style.SUCCESS("Updated Hotel Global Settings."))
            else:
                HotelSettings.objects.create(**settings_data)
                self.stdout.write(self.style.SUCCESS("Created Hotel Global Settings."))

        # 2. Import Currencies (per-item, keyed by iso_code)
        currencies = data.get("currencies", [])
        for c_data in currencies:
            iso_code = c_data.get("iso_code")
            if not iso_code:
                continue
            existing = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=iso_code).first()
            if existing and not do_update:
                self.stdout.write(self.style.WARNING(f"Currency '{iso_code}' already exists. Skipping."))
            elif existing and do_update:
                for field, value in c_data.items():
                    setattr(existing, field, value)
                existing.save()
                self.stdout.write(self.style.SUCCESS(f"Updated currency: {iso_code}"))
            else:
                Currency.objects.create(
                    iso_code=iso_code,
                    name=c_data.get("name"),
                    symbol=c_data.get("symbol"),
                    is_published=c_data.get("is_published", True),
                    sequence=c_data.get("sequence"),
                    is_custom=c_data.get("is_custom", False),
                )
                self.stdout.write(self.style.SUCCESS(f"Created currency: {iso_code}"))

        # 3. Import Navigation Menus (per-item, keyed by name + position)
        menus = data.get("navigation_menus", [])
        if do_update:
            valid_keys = {(m.get("name"), m.get("position")) for m in menus if m.get("name") and m.get("position")}
            for old_menu in NavigationMenu.objects.all():
                if (old_menu.name, old_menu.position) not in valid_keys:
                    old_menu.delete()
                    self.stdout.write(self.style.NOTICE(f"Deleted outdated menu item: {old_menu.name} ({old_menu.position})"))

        for m_data in menus:
            name = m_data.get("name")
            position = m_data.get("position")
            if not name or not position:
                continue
            existing = NavigationMenu.objects.filter(name=name, position=position).first()
            if existing and not do_update:
                self.stdout.write(self.style.WARNING(
                    f"Menu item '{name}' ({position}) already exists. Skipping."
                ))
            elif existing and do_update:
                existing.url = m_data.get("url", existing.url)
                existing.order = m_data.get("order", existing.order)
                existing.is_published = m_data.get("is_published", existing.is_published)
                existing.save()
                self.stdout.write(self.style.SUCCESS(f"Updated menu item: {name} ({position})"))
            else:
                NavigationMenu.objects.create(
                    name=name,
                    position=position,
                    url=m_data.get("url"),
                    order=m_data.get("order", 0),
                    is_published=m_data.get("is_published", True),
                )
                self.stdout.write(self.style.SUCCESS(f"Created menu item: {name} ({position})"))

        # 4. Import SEO Page Banner Defaults (per-item, keyed by path)
        seo_banners = data.get("seo_banners", [])
        for seo in seo_banners:
            path = seo.get("path")
            if not path:
                continue
            existing = SEOData.objects.filter(path=path).first()
            if existing and not do_update:
                self.stdout.write(self.style.WARNING(
                    f"SEO data for '{path}' already exists. Skipping."
                ))
            elif existing and do_update:
                for field, value in seo.items():
                    if field != "path":
                        setattr(existing, field, value)
                existing.save()
                self.stdout.write(self.style.SUCCESS(f"Updated SEO data: {path}"))
            else:
                SEOData.objects.create(**seo)
                self.stdout.write(self.style.SUCCESS(f"Created SEO data: {path}"))

        # 5. Import / Seed Payment Processors (per-item, keyed by code)
        processors = data.get("payment_processors", [])
        if processors:
            from payments.models.payment_processor import PaymentProcessor, PaymentProcessorCurrency
            
            for p_data in processors:
                code = p_data.get("code")
                if not code:
                    continue
                
                existing = PaymentProcessor._base_manager.filter(code=code).first()
                if existing:
                    if do_update:
                        existing.name = p_data.get("name", existing.name)
                        existing.apply_tax = p_data.get("apply_tax", existing.apply_tax)
                        existing.is_published = p_data.get("is_published", existing.is_published)
                        existing.is_active = True
                        existing.deleted_at = None
                        existing.save()
                        self.stdout.write(self.style.SUCCESS(f"Updated payment processor: {code}"))
                    else:
                        if not existing.is_active:
                            existing.is_active = True
                            existing.deleted_at = None
                            existing.save()
                            self.stdout.write(self.style.SUCCESS(f"Restored soft-deleted payment processor: {code}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Payment processor '{code}' already exists. Skipping."))
                    processor = existing
                else:
                    processor = PaymentProcessor.objects.create(
                        name=p_data.get("name"),
                        code=code,
                        apply_tax=p_data.get("apply_tax", True),
                        is_published=p_data.get("is_published", True),
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created payment processor: {code}"))
                
                # Associate currencies
                currency_codes = p_data.get("payment_currencies", [])
                for cc in currency_codes:
                    curr = Currency.objects.get_queryset().set_active_test(enabled=False).filter(iso_code=cc).first()
                    if curr:
                        PaymentProcessorCurrency.objects.get_or_create(
                            payment_processor=processor,
                            currency=curr
                        )

        self.stdout.write(self.style.SUCCESS("Initial data import completed!"))
