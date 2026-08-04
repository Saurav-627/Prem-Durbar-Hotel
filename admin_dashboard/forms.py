from django import forms
from settings_manager.models.hotel_settings import HotelSettings
from payments.models.payment_processor import PaymentProcessor, PaymentProcessorCurrency
from settings_manager.models.navigation import NavigationMenu
from settings_manager.models.currency import Currency
from homepage.models.hero_slide import HeroSlide
from homepage.models.about_preview import AboutPreview
from homepage.models.about_cms import AboutCMS
from homepage.models.zipline_cms import ZiplineCMS
from homepage.models.sustainability_cms import SustainabilityCMS, SustainabilityPillar
from homepage.models.team_member import TeamMember
from rooms.models.room_category import RoomCategory
from rooms.models.room import Room
from rooms.models.room_image import RoomImage
from rooms.models.room_facility import RoomFacility
from rooms.models.room_policy import RoomPolicy
from rooms.models.room_seasonal_price import RoomSeasonalPrice
from booking.models.booking import Booking
from booking.models.coupon import Coupon
from dining.models.item import DiningCategory, DiningItem, DiningItemBasePrice
from gallery.models.category import GalleryCategory
from gallery.models.item import GalleryItem
from contact.models.branch import Branch
from contact.models.inquiry import ContactInquiry
from contact.models.category import ContactInquiryCategory
from testimonials.models.testimonial import Testimonial
from seo.models.seo_data import SEOData
from django.contrib.auth import get_user_model

User = get_user_model()

class TailwindFormMixin:
    """Mixin to inject standard premium Tailwind styling to form widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pyrefly: ignore [missing-attribute]
        for field_name, field in self.fields.items():
            widget = field.widget
            
            # Checkbox Select Multiple
            if isinstance(widget, forms.CheckboxSelectMultiple):
                css_classes = ""
            # Checkbox
            elif isinstance(widget, forms.CheckboxInput):
                if field_name == 'DELETE':
                    css_classes = "rounded border-neutral-300 dark:border-neutral-700 text-brand-primary focus:ring-brand-primary bg-white dark:bg-neutral-800 transition duration-150 ease-in-out cursor-pointer"
                else:
                    css_classes = "sr-only peer"
            # Textarea
            elif isinstance(widget, forms.Textarea):
                css_classes = "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-brand-primary/20 focus:border-brand-primary outline-none transition-all duration-200 h-28"
            # Date/Time input
            elif isinstance(widget, (forms.DateInput, forms.DateTimeInput, forms.TimeInput)):
                css_classes = "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-brand-primary/20 focus:border-brand-primary outline-none transition-all duration-200 cursor-pointer"
            # Standard Select or SelectMultiple
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_classes = "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-brand-primary/20 focus:border-brand-primary outline-none transition-all duration-200 cursor-pointer"
            # File Uploads
            elif isinstance(widget, forms.FileInput):
                if isinstance(widget, forms.ClearableFileInput):
                    widget.template_name = 'admin_dashboard/widgets/custom_clearable_file_input.html'
                css_classes = "block w-full text-sm text-neutral-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-brand-primary/10 file:text-brand-primary dark:file:text-brand-primaryLight hover:file:bg-brand-primary/20 file:cursor-pointer bg-white dark:bg-neutral-800 rounded-lg border border-neutral-300 dark:border-neutral-700 px-3 py-2 transition"
            # Standard Text Inputs
            else:
                css_classes = "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-brand-primary/20 focus:border-brand-primary outline-none transition-all duration-200"
            
            # Apply styling
            existing_class = widget.attrs.get('class', '')
            widget.attrs['class'] = f"{existing_class} {css_classes}".strip()
            
            # Placeholders
            if not widget.attrs.get('placeholder') and field.label:
                widget.attrs['placeholder'] = f"Enter {field.label.lower()}..."

# Forms Definitions

class HotelSettingsForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = HotelSettings
        fields = '__all__'

class NavigationMenuForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = NavigationMenu
        fields = '__all__'

class CurrencyForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Currency
        fields = '__all__'

class HeroSlideForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = '__all__'

class AboutPreviewForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AboutPreview
        fields = '__all__'

class RoomCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomCategory
        fields = '__all__'

from rooms.models.room_base_price import RoomBasePrice

class RoomForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['created_at', 'updated_at']

class RoomBasePriceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomBasePrice
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].required = False
        self.fields['base_price'].required = False
        self.fields['base_price'].label = "Base Price (Regular Rate)"
        self.fields['discount_price'].label = "Discounted Price (Sale Price) (Optional)"
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True)

    def clean(self):
        cleaned_data = super().clean()
        # pyrefly: ignore [missing-attribute]
        currency = cleaned_data.get('currency')
        # pyrefly: ignore [missing-attribute]
        base_price = cleaned_data.get('base_price')
        # pyrefly: ignore [missing-attribute]
        discount_price = cleaned_data.get('discount_price')

        # If one is provided, both must be provided
        if currency and base_price is None:
            self.add_error('base_price', 'Base price is required when currency is selected.')
        elif base_price is not None and not currency:
            self.add_error('currency', 'Currency is required when base price is entered.')

        if base_price and discount_price and discount_price >= base_price:
            self.add_error('discount_price', 'Discount Price must be less than Base Price.')
            
        return cleaned_data

    def has_changed(self):
        # If both fields are submitted empty/blank, treat the form as unchanged so Django ignores it
        prefix = self.prefix
        curr_key = f"{prefix}-currency" if prefix else "currency"
        price_key = f"{prefix}-base_price" if prefix else "base_price"
        
        curr_val = self.data.get(curr_key)
        price_val = self.data.get(price_key)
        
        if not curr_val and not price_val:
            return False
        return super().has_changed()

class RoomImageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = '__all__'

class RoomFacilityForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomFacility
        fields = '__all__'

class RoomPolicyForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomPolicy
        fields = '__all__'

class CurrencyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.iso_code} — {obj.name}"

class RoomPriceForm(TailwindFormMixin, forms.ModelForm):
    currency = CurrencyChoiceField(
        queryset=Currency.objects.all().order_by('sequence', 'name'),
        required=False,
        empty_label="— All Currencies (wildcard) —",
        help_text="Select a specific currency this override applies to, or leave blank to apply to all.",
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Season start date",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Season end date",
    )

    class Meta:
        model = RoomSeasonalPrice
        fields = '__all__'


class BookingForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

class CouponForm(TailwindFormMixin, forms.ModelForm):
    valid_from = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d'],
        widget=forms.DateTimeInput(
            attrs={
                'type': 'text',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-brand-primary/20 focus:border-brand-primary outline-none transition-all duration-200 cursor-pointer air-datepicker-from',
                'placeholder': 'Select start date & time...',
                'autocomplete': 'off',
            }
        ),
    )
    valid_to = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d'],
        widget=forms.DateTimeInput(
            attrs={
                'type': 'text',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-brand-primary/20 focus:border-brand-primary outline-none transition-all duration-200 cursor-pointer air-datepicker-to',
                'placeholder': 'Select expiry date & time...',
                'autocomplete': 'off',
            }
        ),
    )

    class Meta:
        model = Coupon
        exclude = ['use_count']


from booking.models.coupon import CouponMinSpend

class CouponMinSpendForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = CouponMinSpend
        fields = ['currency', 'min_spend']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'name')
        self.fields['currency'].required = False
        self.fields['min_spend'].required = False

    def has_changed(self):
        """Ignore rows where currency or min_spend is blank."""
        prefix = self.prefix
        curr_key = f"{prefix}-currency" if prefix else "currency"
        ms_key = f"{prefix}-min_spend" if prefix else "min_spend"
        if not self.data.get(curr_key) and not self.data.get(ms_key):
            return False
        return super().has_changed()

    def clean(self):
        cleaned_data = super().clean()
        # pyrefly: ignore [missing-attribute]
        currency = cleaned_data.get('currency')
        # pyrefly: ignore [missing-attribute]
        min_spend = cleaned_data.get('min_spend')
        if currency and min_spend is None:
            self.add_error('min_spend', 'Min spend is required when currency is selected.')
        elif min_spend is not None and not currency:
            self.add_error('currency', 'Currency is required when min spend is entered.')
        return cleaned_data

class GalleryCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = GalleryCategory
        fields = '__all__'

class GalleryItemForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = '__all__'

class DiningCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DiningCategory
        fields = '__all__'

class DiningItemForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DiningItem
        fields = ['category', 'title', 'slug', 'description', 'image', 'image_url', 'is_vegetarian', 'is_vegan', 'is_spicy', 'is_chef_special', 'is_published', 'order']


class DiningItemBasePriceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DiningItemBasePrice
        fields = ['currency', 'base_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].required = False
        self.fields['base_price'].required = False
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True)

    def clean(self):
        cleaned_data = super().clean()
        # pyrefly: ignore [missing-attribute]
        currency = cleaned_data.get('currency')
        # pyrefly: ignore [missing-attribute]
        base_price = cleaned_data.get('base_price')

        if currency and base_price is None:
            self.add_error('base_price', 'Base price is required when currency is selected.')
        elif base_price is not None and not currency:
            self.add_error('currency', 'Currency is required when base price is entered.')

        return cleaned_data

    def has_changed(self):
        prefix = self.prefix
        curr_key = f"{prefix}-currency" if prefix else "currency"
        price_key = f"{prefix}-base_price" if prefix else "base_price"

        curr_val = self.data.get(curr_key)
        price_val = self.data.get(price_key)

        if not curr_val and not price_val:
            return False
        return super().has_changed()


class BaseDiningItemBasePriceFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        has_at_least_one_price = False
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            curr = form.cleaned_data.get('currency')
            price = form.cleaned_data.get('base_price')
            if curr and price is not None:
                has_at_least_one_price = True
                break

        if not has_at_least_one_price:
            raise forms.ValidationError("At least one currency price is required for this menu item (e.g. NPR or USD).")


DiningItemBasePriceFormSet = forms.inlineformset_factory(
    DiningItem,
    DiningItemBasePrice,
    form=DiningItemBasePriceForm,
    formset=BaseDiningItemBasePriceFormSet,
    extra=2,
    can_delete=True
)

class BranchForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Branch
        fields = '__all__'

class ContactInquiryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = '__all__'

class TestimonialForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'

class SEODataForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = SEOData
        fields = '__all__'

class UserForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'is_active', 'is_staff', 'is_superuser', 'is_hotel_admin', 'is_guest', 'avatar', 'groups', 'user_permissions']


class PaymentProcessorForm(TailwindFormMixin, forms.ModelForm):
    payment_currencies = forms.ModelMultipleChoiceField(
        queryset=Currency.objects.filter(is_published=True),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Supported Currencies"
    )

    class Meta:
        model = PaymentProcessor
        fields = ['name', 'code', 'apply_tax', 'is_published']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['payment_currencies'].initial = self.instance.payment_currencies.all()

    def save(self, commit=True):
        processor = super().save(commit=commit)
        if commit:
            self.save_currencies(processor)
        else:
            original_save_m2m = self.save_m2m
            def new_save_m2m():
                # pyrefly: ignore [bad-argument-type]
                original_save_m2m()
                self.save_currencies(processor)
            self.save_m2m = new_save_m2m
        return processor

    def save_currencies(self, processor):
        selected_currencies = self.cleaned_data.get('payment_currencies', [])
        PaymentProcessorCurrency.objects.filter(payment_processor=processor).exclude(
            currency__in=selected_currencies
        ).delete()
        for currency in selected_currencies:
            PaymentProcessorCurrency.objects.get_or_create(
                payment_processor=processor,
                currency=currency
            )


class AboutCMSForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AboutCMS
        fields = '__all__'


class ZiplineCMSForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ZiplineCMS
        fields = '__all__'
        widgets = {
            'video_file': forms.ClearableFileInput(attrs={'accept': 'video/*'}),
            'available_time_slots': forms.Textarea(attrs={
                'placeholder': "Morning (09:00 AM - 12:00 PM)\nAfternoon (12:00 PM - 03:00 PM)\nSunset Flight (03:00 PM - 06:00 PM)",
                'rows': 4
            }),
        }


class SustainabilityCMSForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = SustainabilityCMS
        fields = '__all__'


class SustainabilityPillarForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = SustainabilityPillar
        fields = '__all__'


class TeamMemberForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'


from homepage.models.zipline_package import ZiplinePackage, ZiplinePackageBasePrice

class ZiplinePackageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ZiplinePackage
        exclude = ['created_at', 'updated_at']


class ZiplinePackageBasePriceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ZiplinePackageBasePrice
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].required = False
        self.fields['base_price'].required = False
        self.fields['base_price'].label = "Base Price (Regular Rate)"
        self.fields['discount_price'].label = "Discounted Price (Sale Price) (Optional)"
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True)

    def clean(self):
        cleaned_data = super().clean()
        # pyrefly: ignore [missing-attribute]
        currency = cleaned_data.get('currency')
        # pyrefly: ignore [missing-attribute]
        base_price = cleaned_data.get('base_price')
        # pyrefly: ignore [missing-attribute]
        discount_price = cleaned_data.get('discount_price')

        if currency and base_price is None:
            self.add_error('base_price', 'Base price is required when currency is selected.')
        elif base_price is not None and not currency:
            self.add_error('currency', 'Currency is required when base price is entered.')

        if base_price and discount_price and discount_price >= base_price:
            self.add_error('discount_price', 'Discount Price must be less than Base Price.')

        return cleaned_data

    def has_changed(self):
        prefix = self.prefix
        curr_key = f"{prefix}-currency" if prefix else "currency"
        price_key = f"{prefix}-base_price" if prefix else "base_price"

        curr_val = self.data.get(curr_key)
        price_val = self.data.get(price_key)

        if not curr_val and not price_val:
            return False
        return super().has_changed()


class ContactInquiryCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ContactInquiryCategory
        fields = '__all__'


