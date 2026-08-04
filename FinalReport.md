# Prem Durbar — Platform Technical Architecture & CMS Control Report

> **Purpose:** This comprehensive document maps out every aspect of the Prem Durbar Hotel & Nagarkot Zipline web platform. It serves as an authoritative guide for software engineers, hotel administrators, and content editors, detailing CMS control surfaces, multi-currency models, pricing precedence logic, payment integrations, guest data models, and static components.

---

## Table of Contents

1. [Platform Architecture Overview](#1-platform-architecture-overview)
2. [Multi-Currency & Pricing System](#2-multi-currency--pricing-system)
3. [Real Payment Gateway Architecture & Webhooks](#3-real-payment-gateway-architecture--webhooks)
4. [Admin-Controlled Content & CMS Surfaces](#4-admin-controlled-content--cms-surfaces)
   - [Global Hotel Settings](#41-global-hotel-settings)
   - [Navigation System](#42-navigation-system)
   - [Currency Management](#43-currency-management)
   - [Homepage CMS](#44-homepage-cms)
   - [Rooms & Accommodation Chamber Manager](#45-rooms--accommodation-chamber-manager)
   - [Zipline Adventure Packages & CMS](#46-zipline-adventure-packages--cms)
   - [Dining & Gastronomy Menu](#47-dining--gastronomy-menu)
   - [About Us, Sustainability & Branch Offices](#48-about-us-sustainability--branch-offices)
   - [Coupons & Promotional Discounts](#49-coupons--promotional-discounts)
   - [SEO Banners & Page Meta Tags](#410-seo-banners--page-meta-tags)
5. [Guest Checkout & Detailed Financial Breakdown](#5-guest-checkout--detailed-financial-breakdown)
6. [Official PDF / Print Invoice System](#6-official-pdf--print-invoice-system)
7. [Guest & User Submitted Data Models](#7-guest--user-submitted-data-models)
8. [Static Assets & Ergonomics](#8-static-assets--ergonomics)
9. [Developer Quick-Reference & Maintenance Guide](#9-developer-quick-reference--maintenance-guide)

---

## 1. Platform Architecture Overview

Prem Durbar is a modular Django 6 platform built for a luxury resort and zipline adventure destination in Nepal. The codebase is organized into **16 decoupled Django applications**:

```text
Prem-Durbar-Zipline/
├── accounts/           # User authentication & staff permissions
├── admin_dashboard/    # Custom Management Dashboard, formset editors & invoice templates
├── booking/            # Reservation engine (rooms, zipline, checkout & channel manager sync API)
├── contact/            # Guest inquiry forms & branch location handlers
├── dining/             # Food & beverage menu items & multi-currency rates
├── gallery/            # Resort photo gallery bulk uploader
├── homepage/           # Public homepage, hero slides, zipline packages & CMS models
├── payments/           # Payment gateway processors (Stripe, eSewa, Khalti) & Webhook API
├── rooms/              # Suite chambers, facilities, base rates & seasonal pricing
├── seo/                # SEO page banners & meta tags
├── settings_manager/   # Hotel global settings & navigation menus
├── testimonials/       # Guest reviews & rating testimonials
└── core/               # YAML seed data records (21 files) & management commands
```

---

## 2. Multi-Currency & Pricing System

### Currencies Supported
- **NPR (Nepalese Rupee)** — Primary domestic currency.
- **USD (US Dollar)** — International currency.

### Pricing Models
Multi-currency pricing is normalized across dedicated child models linked to main items:
- Rooms: `RoomBasePrice` (`room`, `currency`, `base_price`, `discount_price`)
- Zipline Packages: `ZiplinePackageBasePrice` (`package`, `currency`, `base_price`, `discount_price`)
- Dining Items: `DiningItemBasePrice` (`item`, `currency`, `base_price`)
- Coupons: `CouponMinSpend` (`coupon`, `currency`, `min_spend_amount`)

### Pricing Terms & Field Definitions
- **`base_price` (Base Price - Regular Rate)**: The standard regular price. Displayed with strikethrough styling (`~~NPR 4,500.00~~`) when a discount price is active.
- **`discount_price` (Discounted Price - Sale Price)**: The discounted offer price. Highlighted as the payable price (`NPR 3,500.00`) when present.
- **Form Safeguard**: `discount_price` must strictly be less than `base_price`. Validation in `RoomBasePriceForm` and `ZiplinePackageBasePriceForm` enforces `discount_price < base_price`.

### Price Evaluation Hierarchy (`final_price` property)
When determining the active price to present to guests or charge on checkout:
1. 🥇 **Active Seasonal Price Override** (`active_seasonal`): Checked first for rooms during specified date ranges.
2. 🥈 **Discounted Price** (`discount_price`): Checked second if an offer/sale price is set for the selected currency.
3. 🥉 **Base Price** (`base_price`): Standard regular rate fallback.

---

## 3. Real Payment Gateway Architecture & Webhooks

The platform integrates real payment processors with automated status synchronization:

### 1. Stripe Checkout Service (`payments/services/stripe_payment.py`)
- Creates real Stripe Checkout Sessions with line items, multi-currency conversion, success/cancel callback URLs, and guest metadata.
- **Stripe SDK v15+ Object Handling**: Utilizes `session.to_dict()` for safe dictionary conversion, ensuring compatibility with Stripe Python SDK v15+.

### 2. Stripe Webhook Endpoint (`/payments/webhook/stripe/`)
- Public endpoint (`payments.views.public.stripe_webhook`) processing `checkout.session.completed` events.
- Validates webhook signatures using `STRIPE_WEBHOOK_SECRET`.
- Atomically updates payment records to `status = 'success'` and updates reservation status from `draft` to `confirmed`.

### 3. Local Webhook Forwarding (`make stripe-listen`)
- Pre-configured `Makefile` command invoking `stripe listen --forward-to 127.0.0.1:8000/payments/webhook/stripe/` for rapid local payment testing.

### 4. eSewa & Khalti Integrations (`payments/services/`)
- Native Nepalese digital payment gateways supporting `NPR` transactions with HMAC-SHA256 signature generation and status verification callbacks.

---

## 4. Admin-Controlled Content & CMS Surfaces

### 4.1 Global Hotel Settings
- **Admin Location:** `Settings Manager -> Hotel Global Settings`
- **Model:** `settings_manager/models/hotel_settings.py` (Singleton)
- **Controls:** Hotel brand name, light/dark logos, favicon, admin panel title & logo, site color themes (*Light*, *Dark*, *Luxury Gold*, *Festival*), contact phone, email, address, Google Maps iframe embed, social media links, footer copyright, and footer description.

### 4.2 Navigation System
- **Admin Location:** `Settings Manager -> Navigation`
- **Model:** `settings_manager/models/navigation.py`
- **Controls:** Header and footer navigation links, parent-child dropdown hierarchies, menu sorting sequence, and publication toggles.

### 4.3 Currency Management
- **Admin Location:** `Settings Manager -> Currencies`
- **Model:** `settings_manager/models/currency.py`
- **Controls:** ISO currency codes (`NPR`, `USD`), symbols, default rates, and published state.

### 4.4 Homepage CMS
- **Hero Slides (`homepage/models/hero_slide.py`)**: Slide titles, subtitles, background images, CTA button labels, and target URLs.
- **About Preview (`homepage/models/about_preview.py`)**: Homepage introduction text, experience badges, and featured images.

### 4.5 Rooms & Accommodation Chamber Manager
- **Admin Location:** `Rooms Manager -> Rooms`
- **Models:** `Room`, `RoomCategory`, `RoomFacility`, `RoomBasePrice`, `RoomSeasonalPrice`, `RoomImage`, `RoomPolicy`.
- **Controls:** Room titles, categories, room sizes (sq. ft.), max adults/children occupancy, bed types, total room inventory, facility checklists, optional room highlights (`blank=True, null=True`), tax percentages, multi-currency base/discount prices, and seasonal price overrides.

### 4.6 Zipline Adventure Packages & CMS
- **Admin Location:** `Admin Dashboard -> Zipline Manager`
- **Models:** `ZiplinePackage`, `ZiplinePackageBasePrice`, `ZiplineCMS`.
- **Controls:** Flight package titles, flight types (*Classic Seated*, *Superman*, *Tandem*), durations, highlights, cover images, multi-currency rates (base & discount price), homepage CMS copy, and embedded live action preview video URLs.

### 4.7 Dining & Gastronomy Menu
- **Admin Location:** `Dining Manager -> Menu Items`
- **Models:** `DiningItem`, `DiningCategory`, `DiningItemBasePrice`.
- **Controls:** Food item titles, descriptions, dietary flags (Vegetarian, Vegan, Gluten-Free, Chef Special), category groupings, and multi-currency pricing.

### 4.8 About Us, Sustainability & Branch Offices
- **About CMS (`homepage/models/about_cms.py`)**: Resort history, mission statement, vision, and core values.
- **Team Members (`homepage/models/team_member.py`)**: Management staff names, designations, bio summaries, and photos.
- **Sustainability CMS (`homepage/models/sustainability_cms.py`)**: Eco-initiatives, green policies, and sustainability pillars.
- **Branch Offices (`contact/models/branch.py`)**: Office locations, contact numbers, address lines, and branch map embeds.

### 4.9 Coupons & Promotional Discounts
- **Admin Location:** `Bookings -> Coupons`
- **Model:** `booking/models/coupon.py`
- **Controls:** Promo codes, discount types (*Percentage* vs *Fixed Amount*), discount values, min spend requirements per currency, valid product types (*room*, *zipline*, *all*), usage limits, and expiration dates.

### 4.10 SEO Banners & Page Meta Tags
- **Admin Location:** `Settings Manager -> SEO Pages`
- **Model:** `seo/models/seo_data.py`
- **Controls:** Page title tags, meta descriptions, canonical URLs, OG social media images, and hero header banner images for all 7 main site routes.

---

## 5. Guest Checkout & Detailed Financial Breakdown

When a guest initiates checkout (`/booking/checkout/<booking_uid>/`):

1. **Pre-Checkout Tax Computation**:
   - Computes tax using `room.tax_percentage` for room stays.
   - Saves `subtotal`, `discount`, `tax`, and `total` directly onto the `Booking` record.

2. **Checkout UI Financial Breakdown (`booking/templates/booking/checkout.html`)**:
   - **Subtotal**: Total un-taxed stay or flight amount.
   - **Discount**: Applied promo code discount (highlighted in emerald green).
   - **Tax (e.g. 13%)**: Computed tax amount displayed when `tax > 0`.
   - **Est. Total (incl. tax)**: Highlighted final payable total.

3. **Context-Aware Confirmation Screen (`payments/templates/payments/success.html`)**:
   - Tailors messaging dynamically based on `booking.booking_type`:
     - **Zipline Flights**: Displays *"Zipline Flight Confirmed"*, flight date, time slot, guest name, and waiver consent timestamp.
     - **Room Stays**: Displays *"Reservation Confirmed"*, suite title, check-in date, check-out date, and guest details.

---

## 6. Official PDF / Print Invoice System

The invoice view (`admin_dashboard/templates/admin_dashboard/bookings/invoice.html`) generates print-ready official receipts:

1. **Line Item Pricing**:
   - Displays unit count (e.g. `1 room(s) x 2 night(s)` or `2 ticket(s)`).
   - Displays active charged rate alongside strikethrough regular base rate.

2. **Special Rate Badges**:
   - **Seasonal Overrides**: Displays `🏷️ Seasonal Price: <Season Name>`.
   - **Special Offers**: Displays `🏷️ Special Offer Discount` for discounted rates.

3. **Financial Summary Table**:
   - Subtotal, Applied Coupon Discount, Standard VAT/Tax, and Total Charged.
   - Payment transaction history table listing gateway name, transaction ID, date, and status.

---

## 7. Guest & User Submitted Data Models

The following models store data submitted by website visitors (read-only for staff):

1. **Bookings (`booking/models/booking.py`)**:
   - `booking_uid`: Unique UUID reference (e.g. `BK-799BBC99`).
   - `booking_type`: `room` or `zipline`.
   - `guest_name`, `guest_email`, `guest_phone`, `special_requests`.
   - `check_in`, `check_out` (Rooms) / `flight_date`, `slot_time` (Zipline).
   - `waiver_accepted`, `waiver_accepted_at`: Legal liability waiver consent proof for zipline flights.
   - `subtotal`, `discount`, `tax`, `total`, `currency_code`.
   - `status`: `draft`, `pending`, `confirmed`, `completed`, `cancelled`.

2. **Payments (`payments/models/payment.py`)**:
   - Payment logs linking `booking`, `gateway` (Stripe, eSewa, Khalti), `transaction_id`, `amount`, `currency`, `tax_amount`, `status`, and gateway raw response JSON.

3. **Contact Inquiries (`contact/models/contact.py`)**:
   - Guest contact submissions containing name, email, phone, subject, category, message, IP address, and read/replied status flags.

---

## 8. Static Assets & Ergonomics

1. **Datepicker Ergonomics (`templates/base.html`)**:
   - AirDatepicker inputs set with `readOnly = true` and `inputmode = "none"` to prevent touch keyboards from obscuring date selection on mobile devices.
   - Dynamic boundary clamping script prevents popups from extending beyond viewport edges.

2. **Passive Touch Listeners**:
   - Mobile carousel swiping equipped with `@touchstart.passive` and `@touchend.passive` listeners to eliminate browser console scroll warnings.

3. **Optional Room Highlights**:
   - `Room.highlights` field made optional (`blank=True, null=True`), ensuring clean room suite creation in admin without requiring highlight bullets.

---

## 9. Developer Quick-Reference & Maintenance Guide

### Common Commands (`Makefile`)

```bash
# Start local Django development server
make run

# Start Stripe webhook listener forwarding to local app
make stripe-listen

# Run database migrations
uv run python manage.py migrate

# Seed or refresh initial database records from YAML
uv run python manage.py seed_data --update

# Validate Django system state
uv run python manage.py check
```

### Essential Settings Key Reference (`.env`)

```env
SECRET_KEY=...
DEBUG=True
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```
