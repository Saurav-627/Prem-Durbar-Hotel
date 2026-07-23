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

Supported Currencies: **NPR**, **USD**, **EUR**, **GBP**, **INR**.

| Field | Description |
|---|---|
| `iso_code` | e.g. USD, NPR, EUR, GBP, INR |
| `name` | e.g. "US Dollar", "Nepalese Rupee" |
| `symbol` | e.g. $, Rs., €, £, ₹ |
| `sequence` | Display order in the currency switcher dropdown |
| `is_published` | Show/hide currency from the frontend switcher |

> **Multi-Currency Pricing Architecture:**
> - **Rooms (`RoomBasePrice`)**: Staff can set nightly base and discount rates per currency.
> - **Dining Food Items (`DiningItemBasePrice`)**: Staff can set food item prices in multiple currencies via an inline formset (at least one currency price is required).
> - **Frontend Switcher**: Server-side cookie-driven currency switcher instantly formats prices across rooms and dining items.

---

### 4. Homepage — Hero Slides
**Admin path:** `CMS Content -> Hero Slides`
**Model:** `homepage/models/hero_slide.py`

The full-screen carousel at the top of the homepage:

| Field | Description |
|---|---|
| `title` | Main large heading on the slide |
| `subtitle` | Smaller supporting text |
| `background_image` | Upload a hero background photo |
| `background_video_url` | YouTube or MP4 video link as background |
| `overlay_opacity` | Dark overlay strength (0.00 - 1.00) |
| `cta_text` | First call-to-action button label |
| `cta_url` | First button link (e.g. /rooms/) |
| `cta2_text` | Second button label |
| `cta2_url` | Second button link (e.g. /booking/) |
| `order` | Slide display order |
| `is_active` | Toggle individual slide on/off |

---

### 5. Homepage — About Preview
**Admin path:** `CMS Content -> About Preview (Homepage)`
**Model:** `homepage/models/about_preview.py`
**Type:** Singleton (only one record)

The "About the Hotel" intro section on the main homepage `/`:

| Field | Description |
|---|---|
| `title` | Section heading (e.g. "Nepal's Premier Adventure & Luxury Resort") |
| `subtitle` | Supporting tagline |
| `content` | Main descriptive paragraph |
| `image` | Featured photo shown in the about section |
| `video_url` | Promo video YouTube/Vimeo link |
| `stat1_value / stat1_label` | First stat counter (e.g. "36" / "Chambers & Suites") |
| `stat2_value / stat2_label` | Second stat counter (e.g. "1" / "Longest Zipline in Nepal") |
| `stat3_value / stat3_label` | Third stat counter (e.g. "100%" / "Organic Farm-to-Table") |
| `stat4_value / stat4_label` | Fourth stat counter (e.g. "5k+" / "Happy Adventurers") |

---

### 6. Rooms & Accommodation
**Admin path:** `Rooms -> Rooms`
**Models:** `rooms/models/room.py`, `room_category.py`, `room_image.py`, `room_facility.py`, `room_seasonal_price.py`, `room_policy.py`, `room_availability.py`, `room_base_price.py`

#### Room (Main Record)
| Field | Description |
|---|---|
| `title` | Room name (e.g. "Deluxe Room Jungle View") |
| `category` | ForeignKey to Room Category |
| `description` | Full room description |
| `highlights` | Bullet highlights |
| `tax_percentage` | VAT/tax rate (default 13%) |
| `room_size` | Size in sq. ft. or sq. meters |
| `max_adults / max_children` | Guest capacities |
| `bed_type` | e.g. "King Size", "Twin" |
| `facilities` | Linked room facilities (many-to-many) |
| `is_featured` | Pin to "Featured Rooms" on homepage |
| `is_published` | Show/hide room from listings |

#### Room Base Price (Inline on Room form)
| Field | Description |
|---|---|
| `currency` | Linked currency (USD / NPR / EUR / GBP / INR) |
| `base_price` | Standard nightly base price |
| `discount_price` | Optional discounted price |

---

### 7. Dining Items & Food Menu
**Admin path:** `Dining Items -> Food Menu Items`
**Models:** `dining/models/item.py` (`DiningCategory`, `DiningItem`, `DiningItemBasePrice`)

| Field | Description |
|---|---|
| `category` | Category FK (e.g. "Nepali Khaja & Thali", "Starters", "Soups & Salads") |
| `title` | Dish name (e.g. "Prem Durbar Special Mutton Thali Set") |
| `slug` | Auto-generated URL slug |
| `description` | Full ingredients & dish description |
| `image / image_url` | Photo upload or image URL |
| `is_vegetarian` | Veg badge tag |
| `is_vegan` | Vegan badge tag |
| `is_spicy` | Spicy badge tag |
| `is_chef_special` | Chef's Special badge tag |
| `is_published` | Show/hide from food menu listings |

#### Dining Item Base Price (Inline Formset)
| Field | Description |
|---|---|
| `currency` | Linked currency (USD / NPR / EUR / GBP / INR) |
| `base_price` | Dish price in specified currency (at least 1 required) |

---

### 8. About Us, Zipline & Sustainability CMS
**Admin path:** `CMS Content -> About Us Page CMS / Zipline CMS & Video / Sustainability CMS`
**Models:** `homepage/models/about_cms.py`, `zipline_cms.py`, `sustainability_cms.py`

#### About Us Page CMS (`AboutCMS`)
| Field | Description |
|---|---|
| `hero_subtitle / hero_title / hero_description` | Hero banner text for `/about/` |
| `story_subtitle / story_title / story_content` | Valley Artistry story section text |
| `video_url` | Optional promo tour video link |

#### Zipline Adventure Page CMS (`ZiplineCMS`)
| Field | Description |
|---|---|
| `hero_subtitle / hero_title / hero_description` | Hero banner text for `/zipline/` |
| `video_file` | Upload MP4 video file to play on live Zipline page |
| `video_url` | External YouTube/Vimeo embed URL for video preview player |
| `spec_length / spec_speed / spec_elevation / spec_safety` | Flight specification badges |
| `overview_subtitle / overview_title / overview_content` | Zipline flight overview body text |

#### Sustainability Page CMS (`SustainabilityCMS` & `SustainabilityPillar`)
| Field | Description |
|---|---|
| `hero_subtitle / hero_title / hero_description` | Banner text for `/sustainability/` |
| `intro_subtitle / intro_title` | Section headers for sustainability pillars |
| `SustainabilityPillar` | Individual pillars (Icon class, Title, Description, Display Order, Published status) |

---

### 9. Gallery
**Admin path:** `CMS Content -> Gallery bulk`
**Models:** `gallery/models/category.py`, `gallery/models/item.py`

---

### 10. Conference & Event Venues
**Admin path:** `Conference -> Event Venues`
**Model:** `conference/models/venue.py`

---

### 11. Contact — Branch Offices
**Admin path:** `Contact -> Hotel Branches`
**Model:** `contact/models/branch.py`

---

### 12. Blog Posts
**Admin path:** `Blogs -> Blog Posts`
**Model:** `blogs/models/post.py`

---

### 13. Nearby Places & Attractions
**Admin path:** `Nearby Places -> Attractions`
**Model:** `nearby_places/models/attraction.py`

---

### 14. Testimonials & Reviews
**Admin path:** `CMS Content -> Testimonials`
**Model:** `testimonials/models/testimonial.py`

---

### 15. Booking Coupons & Discounts
**Admin path:** `Booking -> Coupons`
**Model:** `booking/models/coupon.py`

---

### 16. SEO & Page Banners
**Admin path:** `CMS Content -> SEO Meta tags`
**Model:** `seo/models/seo_data.py`

---

### 17. User Accounts
**Admin path:** `Accounts -> Users`

---

## Guest/User-Submitted Data (Read-Only in Admin)

| Data | Admin Path | What Admin Can Do |
|---|---|---|
| Room Bookings | `Booking -> Bookings` | View details, change status (Pending / Confirmed / Checked In / Checked Out / Cancelled) |
| Payments | `Payments -> Payments` | View gateway, transaction ID, amount, status, raw gateway response (read-only) |
| Conference/Event Inquiries | `Conference -> Event Inquiries` | View guest, venue, event date, catering needs, notes; update status |
| Contact Inquiries | `Contact -> Contact Inquiries` | View name, email, subject, message, category (read-only) |

---

## Static / Hardcoded Content

| Item | Location | Notes |
|---|---|---|
| Payment gateways | `payments/models/payment.py` | Stripe, eSewa, Khalti — hardcoded choices |
| Booking status flow | `booking/models/booking.py` | Pending / Confirmed / Checked In / Checked Out / Cancelled |
| Hero banner fallback text | All listing templates | Default subtitle/title/description when no SEO record is set |
| Page URL routing | Each app's `urls.py` | URL patterns like `/rooms/<slug>/` — developer-managed |
| TailwindCSS design tokens | `static/` and tailwind config | Green nature palette, typography, spacing |
| Alpine.js theme logic | `templates/base.html` | Light/Dark/Luxury/Festival theme switcher |

---

## Summary Table

| Section | Admin Controlled | Guest Submitted | Static / Hardcoded |
|---|:---:|:---:|:---:|
| Hotel name, logos, favicon, admin title & label, theme | YES | | |
| Navigation menus | YES | | |
| Currencies (NPR, USD, EUR, GBP, INR) | YES | | |
| Homepage hero slides | YES | | |
| Homepage about section (`AboutPreview`) | YES | | |
| About Us Page CMS (`AboutCMS`) | YES | | |
| Zipline CMS & Video Player (`ZiplineCMS`) | YES | | |
| Sustainability CMS & Pillars | YES | | |
| Rooms (content, pricing, images) | YES | | |
| Room seasonal prices | YES | | |
| Room policies & facilities | YES | | |
| Dining Food Items & Multi-Currency Prices | YES | | |
| Gallery (photos/videos) | YES | | |
| Conference/event venues | YES | | |
| Contact branch offices | YES | | |
| Blog posts | YES | | |
| Nearby attractions | YES | | |
| Guest testimonials | YES | | |
| Discount coupons | YES | | |
| Page SEO & banner text/image | YES | | |
| User accounts | YES | | |
| Room bookings | | YES (admin manages status) | |
| Payments | | YES (read-only in admin) | |
| Conference inquiries | | YES (admin manages status) | |
| Contact form messages | | YES (read-only in admin) | |

---

*Updated: July 2026 | Prem Durbar Platform v1.0*
