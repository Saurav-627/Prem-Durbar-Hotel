# Prem Durbar — CMS & Admin Control Report

> **Purpose:** This document maps out every part of the Prem Durbar platform — what the admin can control through the Django Admin & Custom Admin Dashboard CMS, what is submitted by guests/users, and what is hardcoded/static in the codebase. Intended for developers, hotel managers, and content editors.

---

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Admin-Controlled Content (CMS)](#admin-controlled-content-cms)
   - [Global Hotel Settings](#1-global-hotel-settings)
   - [Navigation Menus](#2-navigation-menus)
   - [Currency & Multi-Currency Pricing](#3-currency--multi-currency-pricing)
   - [Homepage — Hero Slides](#4-homepage--hero-slides)
   - [Homepage — About Preview](#5-homepage--about-preview)
   - [Rooms & Accommodation](#6-rooms--accommodation)
   - [Dining Items & Food Menu](#7-dining-items--food-menu)
   - [About Us, Zipline & Sustainability CMS](#8-about-us-zipline--sustainability-cms)
   - [Gallery](#9-gallery)
   - [Conference & Event Venues](#10-conference--event-venues)
   - [Contact — Branch Offices](#11-contact--branch-offices)
   - [Blog Posts](#12-blog-posts)
   - [Nearby Places & Attractions](#13-nearby-places--attractions)
   - [Testimonials & Reviews](#14-testimonials--reviews)
   - [Booking Coupons & Discounts](#15-booking-coupons--discounts)
   - [SEO & Page Banners](#16-seo--page-banners)
   - [User Accounts](#17-user-accounts)
3. [Guest/User-Submitted Data (Read-Only in Admin)](#guestuser-submitted-data-read-only-in-admin)
4. [Static / Hardcoded Content](#static--hardcoded-content)
5. [Summary Table](#summary-table)

---

## Platform Overview

Prem Durbar is a full-stack Django CMS platform for a luxury 5-star hotel and adventure resort. It is split into **16 Django apps**, each managing a separate domain of hotel operations. The custom admin portal at `/admin-dashboard/` provides custom CRUD tabs for settings, rooms, food menus, CMS content, and analytics.

---

## Admin-Controlled Content (CMS)

### 1. Global Hotel Settings
**Admin path:** `Settings Manager -> Hotel Global Settings`
**Model:** `settings_manager/models/hotel_settings.py`
**Type:** Singleton (only one record allowed)

The admin can control the entire site-wide identity from one place:

| Field | What it controls |
|---|---|
| `site_name` | Hotel name shown across all user and admin pages |
| `logo` | Light mode main logo image |
| `logo_dark` | Dark mode logo variant |
| `favicon` | Browser tab icon (`.png`, `.ico`, `.svg`) |
| `admin_logo` | Admin dashboard panel logo (falls back to main logo if un-set) |
| `admin_title` | Admin panel browser tab title |
| `admin_label` | Admin panel sidebar brand title label |
| `theme` | Default site theme: Light / Dark / Luxury Gold / Festival |
| `contact_phone` | Phone number shown in header, footer, and invoice |
| `contact_email` | Email shown in header, footer, and invoice |
| `address` | Hotel address shown in footer, contact page, and invoice |
| `google_maps_iframe` | Embedded Google Maps on contact/branch pages |
| `facebook_url` | Facebook social link in footer |
| `instagram_url` | Instagram social link in footer |
| `twitter_url` | Twitter social link in footer |
| `youtube_url` | YouTube social link in footer |
| `tripadvisor_url` | Tripadvisor social link in footer |
| `about_text` | Short hotel description shown in footer |
| `copyright_text` | Footer copyright line |

---

### 2. Navigation Menus
**Admin path:** `Settings Manager -> Navigation`
**Model:** `settings_manager/models/navigation.py`

The admin can fully manage all navigation links site-wide without touching code:

| Field | Description |
|---|---|
| `name` | Display label of the menu item |
| `url` | Internal path (e.g. `/rooms/`) or external URL |
| `position` | Where it appears: Header, Footer Quick Links, Footer Services, Footer OTA Partners |
| `order` | Sort order among menu items |
| `parent` | Nest under a parent item (dropdown support) |
| `is_published` | Toggle visibility instantly |

---

### 3. Currency & Multi-Currency Pricing
**Admin path:** `Settings Manager -> Currencies`
**Model:** `settings_manager/models/currency.py`

Supported Currencies: **NPR (Nepalese Rupee)** and **USD (US Dollar)**.

| Field | Description |
|---|---|
| `iso_code` | e.g. USD, NPR |
| `name` | e.g. "US Dollar", "Nepalese Rupee" |
| `symbol` | e.g. $, Rs. |
| `sequence` | Display order in currency switcher |
| `is_published` | Publish/unpublish currency across site |

---

### 4. Homepage — Hero Slides
**Admin path:** `Homepage Manager -> Hero Slides`
**Model:** `homepage/models/hero_slide.py`

| Field | Description |
|---|---|
| `title` | Hero main heading |
| `subtitle` | Small uppercase text above heading |
| `description` | Subheading description paragraph |
| `background_image` | Fullscreen background image |
| `cta_primary_text` / `cta_primary_url` | Primary button text & link |
| `cta_secondary_text` / `cta_secondary_url` | Secondary button text & link |
| `order` | Slide sequence order |
| `is_active` | Enable/disable slide |

---

### 5. Rooms & Accommodation
**Admin path:** `Rooms Manager -> Rooms`
**Models:** `rooms/models/` (`Room`, `RoomCategory`, `RoomFacility`, `RoomBasePrice`, `RoomSeasonalPrice`, `RoomImage`, `RoomPolicy`)

| Field | Description |
|---|---|
| `title` / `slug` | Chamber title and URL slug |
| `category` | Chamber category (Standard, Family, Deluxe) |
| `description` | Chamber detailed description |
| `room_size` | Size in square feet |
| `bed_type` | Bed configuration label |
| `max_adults` / `max_children` | Occupancy caps |
| `total_rooms` | Total physical room inventory |
| `facilities` | Linked room amenities checklist |
| `base_prices` | Multi-currency base pricing (NPR, USD) |
| `seasonal_prices` | Overriding seasonal date range pricing |
| `images` | Gallery photos |
| `policies` | House rules, check-in/out policies |

---

### 6. Zipline Packages & CMS
**Admin path:** `Admin Dashboard -> Zipline Manager`
**Models:** `homepage/models/zipline_package.py`, `homepage/models/zipline_cms.py`

| Field | Description |
|---|---|
| `name` / `slug` | Flight package name & URL slug |
| `flight_type` | Category flight harness type (*Classic Seated*, *Superman*, *Tandem*) |
| `duration` | Flight duration & distance specs |
| `description` / `highlights` | Flight overview & bullet points |
| `image_url` | Flight cover image |
| `base_prices` | Multi-currency rates in NPR & USD |
| `homepage_heading` / `homepage_description` | CMS copy for homepage zipline section |
| `video_url` | Embedded YouTube/Vimeo action flight preview |

---

## Guest/User-Submitted Data (Read-Only in Admin)

1. **Bookings (`booking/models/booking.py`)**:
   - `booking_reference`: Unique UUID tracking code (e.g., `BK-8F3A1C9D`).
   - `booking_type`: Room chamber vs. Zipline flight package.
   - `guest_name`, `guest_email`, `guest_phone`: Contact specs.
   - `check_in`, `check_out` / `flight_date`: Travel dates.
   - `total_price`, `currency`: Total payable amount & currency.
   - `payment_status`: Payment transaction state (`draft`, `pending`, `paid`, `cancelled`).

2. **Payments (`payments/models/payment.py`)**:
   - Transaction reference UUIDs, gateway responses (Stripe, eSewa, Khalti), status timestamps.

3. **Contact Inquiries (`contact/models/contact.py`)**:
   - Guest inquiry name, email, phone, message content, status (`unread`, `read`, `replied`).

---

## Static / Hardcoded Content

1. **Brand Logos**: Fallback logo asset at `static/images/hotel-logo.png` when no custom logo is uploaded in `HotelSettings`.
2. **Template Layout Grid System**: Responsive layout structures, dynamic theme colors (`Light`, `Dark`, `Luxury Gold`, `Festival`), and safe-area insets.
3. **AirDatepicker Ergonomics**: `readOnly` input handling and dynamic left/right space tracking function in `base.html`.

---

## Summary Table

| Feature / Module | Admin CMS Controlled | User Submitted | Static Asset Fallback |
|---|---|---|---|
| Hotel Branding & Theme | YES | NO | `hotel-logo.png` |
| Multi-Currency Rates (NPR, USD) | YES | NO | Default USD |
| Room Suites & Seasonal Rates | YES | NO | Default pricing |
| Zipline Packages & Flight Rates | YES | NO | Default pricing |
| Room & Zipline Bookings | NO | YES | N/A |
| Contact & Concierge Messages | NO | YES | N/A |
