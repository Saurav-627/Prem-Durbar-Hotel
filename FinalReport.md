# Prem Durbar — CMS & Admin Control Report

> **Purpose:** This document maps out every part of the Prem Durbar platform — what the admin can control through the Django Admin CMS, what is submitted by guests/users, and what is hardcoded/static in the codebase. Intended for developers, hotel managers, and content editors.

---

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Admin-Controlled Content (CMS)](#admin-controlled-content-cms)
   - [Global Hotel Settings](#1-global-hotel-settings)
   - [Navigation Menus](#2-navigation-menus)
   - [Currency Management](#3-currency-management)
   - [Homepage — Hero Slides](#4-homepage--hero-slides)
   - [Homepage — About Preview](#5-homepage--about-preview)
   - [Rooms & Accommodation](#6-rooms--accommodation)
   - [Dining Venues](#7-dining-venues)
   - [Recreation & Activities](#8-recreation--activities)
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

Prem Durbar is a full-stack Django CMS platform for a luxury 5-star hotel. It is split into **16 Django apps**, each managing a separate domain of hotel operations. The admin panel is powered by **Django Unfold** for a modern UI. The frontend uses **TailwindCSS** and **Alpine.js**.

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

> **Note:** Adding/removing/reordering any navigation item takes effect on the live website immediately — no code change needed.

---

### 3. Currency Management
**Admin path:** `Settings Manager -> Currencies`
**Model:** `settings_manager/models/currency.py`

| Field | Description |
|---|---|
| `iso_code` | e.g. USD, NPR, EUR, GBP |
| `name` | e.g. "US Dollar" |
| `symbol` | e.g. $, Rs, EUR |
| `sequence` | Display order in the currency switcher dropdown |
| `is_published` | Show/hide currency from the frontend switcher |

> The currency switcher is cookie-driven and persists the guest's choice across pages. Room prices are displayed in the selected currency.

---

### 4. Homepage — Hero Slides
**Admin path:** `Homepage -> Hero Slides`
**Model:** `homepage/models/hero_slide.py`

The full-screen carousel at the top of the homepage. Admin can manage unlimited slides:

| Field | Description |
|---|---|
| `title` | Main large heading on the slide |
| `subtitle` | Smaller supporting text |
| `background_image` | Upload a hero background photo |
| `background_video_url` | YouTube or MP4 video link as background |
| `overlay_opacity` | Dark overlay strength (0.00 - 1.00) |
| `cta_text` | First call-to-action button label (e.g. "Discover More") |
| `cta_url` | First button link (e.g. /rooms/) |
| `cta2_text` | Second button label (e.g. "Book Now") |
| `cta2_url` | Second button link (e.g. /booking/) |
| `title_animation` | Entry animation: Fade In Down / Fade In Up / Zoom In / Slide In |
| `subtitle_animation` | Entry animation for subtitle |
| `order` | Slide display order |
| `is_active` | Toggle individual slide on/off |

---

### 5. Homepage — About Preview
**Admin path:** `Homepage -> About Preview`
**Model:** `homepage/models/about_preview.py`
**Type:** Singleton (only one record)

The "About the Hotel" section below the hero slider:

| Field | Description |
|---|---|
| `title` | Section heading (e.g. "About Prem Durbar") |
| `subtitle` | Supporting tagline |
| `content` | Main descriptive paragraph |
| `image` | Featured photo shown in the about section |
| `video_url` | Promo video YouTube/Vimeo link |
| `stat1_value / stat1_label` | First stat counter (e.g. "120" / "Luxury Rooms") |
| `stat2_value / stat2_label` | Second stat counter (e.g. "5" / "Star Rating") |
| `stat3_value / stat3_label` | Third stat counter (e.g. "3" / "Elite Restaurants") |
| `stat4_value / stat4_label` | Fourth stat counter (e.g. "15+" / "Awards Won") |

---

### 6. Rooms & Accommodation
**Admin path:** `Rooms -> Rooms`
**Models:** `rooms/models/room.py`, `room_category.py`, `room_image.py`, `room_facility.py`, `room_seasonal_price.py` (renamed from `room_price.py`), `room_policy.py`, `room_availability.py`, `room_base_price.py` (renamed from `room_currency_price.py`)

This is the core of the platform. Admin has full control over:

#### Room (Main Record)
| Field | Description |
|---|---|
| `title` | Room name (e.g. "Deluxe King Suite") |
| `category` | ForeignKey to Room Category (managed dynamically in admin) |
| `description` | Full room description |
| `highlights` | Comma-separated or line-separated bullet highlights |
| `tax_percentage` | VAT/tax rate (default 13%) |
| `room_size` | Size in sq. ft. or sq. meters |
| `max_adults` | Maximum adult guests |
| `max_children` | Maximum child guests |
| `bed_type` | e.g. "King Size", "Twin" |
| `facilities` | Linked room facilities (many-to-many) |
| `virtual_tour_url` | Link to a 3D virtual tour |
| `video_url` | YouTube/Vimeo embed for room video |
| `is_featured` | Pin to "Featured Rooms" section on homepage |
| `is_published` | Show/hide room from listings |


#### Room Base Price (ForeignKey linked to Room, managed in admin)
| Field | Description |
|---|---|
| `currency` | Linked currency (USD / NPR / EUR / GBP) |
| `base_price` | Standard nightly base price for the currency |
| `discount_price` | Optional discounted price for the currency |

#### Room Images (Inline on Room form)
| Field | Description |
|---|---|
| `image` | Upload gallery photos for the room |
| `is_primary` | Designate the main thumbnail |
| `alt_text` | Accessibility description |

#### Room Seasonal Prices (Inline on Room form)
| Field | Description |
|---|---|
| `name` | e.g. "Christmas Season", "Summer Special" |
| `currency` | Optional currency override. Leave blank to apply as wildcard to all currencies. |
| `start_date / end_date` | Date range for the special price |
| `price_override` | Price per night during this period |
| `is_active` | Enable/disable the seasonal price |

#### Room Policies (Inline on Room form)
| Field | Description |
|---|---|
| `title` | Policy name (e.g. "Cancellation Policy", "Pet Policy") |
| `description` | Full policy text |

#### Room Facilities
**Admin path:** `Rooms -> Room Facilities`
| Field | Description |
|---|---|
| `name` | Facility name (e.g. "Free Wi-Fi", "Air Conditioning") |
| `icon_class` | FontAwesome icon class |
| `svg_path` | Custom SVG code for rendering icons |
| `is_featured` | Show in the featured amenities strip |

#### Room Availability
**Admin path:** `Rooms -> Room Availability`
| Field | Description |
|---|---|
| `room` | Which room |
| `date` | Specific calendar date |
| `is_available` | Mark as available or blocked |
| `booking` | Linked booking record (auto-set when booked) |

---

### 7. Dining Venues
**Admin path:** `Dining -> Dining Venues`
**Model:** `dining/models/venue.py`

| Field | Description |
|---|---|
| `name` | Restaurant/bar name |
| `category` | Restaurant / Bar & Lounge / Cafe / Rooftop / Pool Bar / Fine Dining |
| `description` | Full venue description |
| `timings` | Opening hours (e.g. "7:00 AM - 11:00 PM") |
| `menu_pdf` | Upload a PDF menu |
| `chef_name` | Head chef's name |
| `chef_bio` | Chef biography |
| `chef_image` | Chef photo |
| `capacity` | Guest seating capacity |
| `featured_dishes` | Comma-separated signature dishes |
| `video_url` | Virtual tour or venue intro video |
| `image` | Venue cover photo |
| `is_featured` | Feature on homepage |
| `is_published` | Show/hide from dining listings |

---

### 8. Recreation & Activities
**Admin path:** `Recreation -> Recreation & Activities`
**Model:** `recreation/models/activity.py`

| Field | Description |
|---|---|
| `name` | Activity name (e.g. "Infinity Pool", "Ayurvedic Spa") |
| `category` | Spa / Pool / Gym / Kids Zone / Casino / Adventure / Safari / Games |
| `description` | Full description |
| `timings` | Hours of operation |
| `price_info` | Price string (e.g. "$50/Session" or "Complimentary for Guests") |
| `capacity` | Maximum guests at a time |
| `image` | Activity cover photo |
| `is_active` | Show/hide from listings |

---

### 9. Gallery
**Admin path:** `Gallery -> Gallery Categories` and `Gallery -> Gallery Items`
**Models:** `gallery/models/category.py`, `gallery/models/item.py`

#### Gallery Categories
| Field | Description |
|---|---|
| `name` | Category name (e.g. "Rooms", "Pool", "Dining") |
| `slug` | Auto-generated URL slug |
| `is_published` | Show/hide category tab from gallery page |

#### Gallery Items
| Field | Description |
|---|---|
| `category` | Which category this media belongs to |
| `image` | Upload a photo (auto-generates thumbnail via imagekit) |
| `caption` | Image/video description |
| `is_video` | Mark as a video item instead of photo |
| `is_drone` | Tag as aerial/drone footage |
| `video_url` | YouTube, Vimeo, or direct video URL |
| `virtual_tour_url` | 360 degree virtual tour embed link |
| `is_published` | Show/hide individual item |

---

### 10. Conference & Event Venues
**Admin path:** `Conference -> Event Venues`
**Model:** `conference/models/venue.py`

| Field | Description |
|---|---|
| `name` | Venue hall name (e.g. "Grand Ballroom") |
| `description` | Detailed venue description |
| `capacity` | Maximum seating/floating capacity |
| `layout_options` | Layout text (e.g. "Theatre: 300, Classroom: 150, Banquet: 200") |
| `base_price` | Starting rental price |
| `image` | Venue hall photo |
| `is_active` | Show/hide from venue listings |

---

### 11. Contact — Branch Offices
**Admin path:** `Contact -> Hotel Branches`
**Model:** `contact/models/branch.py`

| Field | Description |
|---|---|
| `name` | Branch name (e.g. "Head Office", "Airport Office") |
| `address` | Full address |
| `phone` | Branch contact number |
| `email` | Branch email |
| `maps_iframe` | Google Maps embed HTML for this location |
| `is_main` | Mark as the main/primary branch |
| `is_published` | Show/hide on the contact page |

---

### 12. Blog Posts
**Admin path:** `Blogs -> Blog Posts`
**Model:** `blogs/models/post.py`

| Field | Description |
|---|---|
| `title` | Blog post title |
| `slug` | Auto-generated URL slug |
| `content` | Full article content |
| `featured_image` | Cover photo for the post |
| `author` | Linked admin user |
| `is_active` | Show/hide post from blog listing |

---

### 13. Nearby Places & Attractions
**Admin path:** `Nearby Places -> Attractions`
**Model:** `nearby_places/models/attraction.py`

| Field | Description |
|---|---|
| `name` | Attraction name (e.g. "Chitwan National Park") |
| `category` | Airport / National Park / Religious Site / Tourist Attraction / Border / City |
| `distance` | e.g. "15 km" |
| `travel_time` | e.g. "20 minutes drive" |
| `maps_url` | Google Maps directions link |
| `image` | Photo of the attraction |
| `description` | Description text |
| `order` | Display order |
| `is_active` | Show/hide from the nearby places section |

---

### 14. Testimonials & Reviews
**Admin path:** `Testimonials -> Testimonials`
**Model:** `testimonials/models/testimonial.py`

| Field | Description |
|---|---|
| `guest_name` | Name of the reviewer |
| `guest_image` | Guest photo (optional) |
| `country` | Guest's country (e.g. "United Kingdom") |
| `source` | Platform: Google / Booking.com / Agoda / Tripadvisor / Direct |
| `rating` | Star rating (1-5) |
| `review_text` | Full review quote |
| `is_featured` | Show in the homepage featured reviews strip |
| `is_published` | Show/hide globally |

---

### 15. Booking Coupons & Discounts
**Admin path:** `Booking -> Coupons`
**Model:** `booking/models/coupon.py`

| Field | Description |
|---|---|
| `code` | Promo code string (e.g. "SUMMER25") |
| `discount_type` | Percentage (%) or Fixed Amount |
| `discount_value` | Amount of discount |
| `min_spend` | Minimum booking value to apply the coupon |
| `valid_from / valid_to` | Coupon active date range |
| `is_active` | Enable/disable coupon immediately |

---

### 16. SEO & Page Banners
**Admin path:** `SEO -> SEO Page Data`
**Model:** `seo/models/seo_data.py`

Each URL path on the site can have its own SEO configuration and custom hero banner:

#### Page Identity
| Field | Description |
|---|---|
| `path` | Exact URL path (e.g. `/rooms/`, `/contact/`) |
| `meta_title` | Browser tab title and search engine title |
| `meta_description` | Search engine snippet (max 160 chars) |
| `canonical_url` | Custom canonical URL (leave blank to auto-set) |

#### Banner Header
| Field | Description |
|---|---|
| `header_subtitle` | Small uppercase label above the main title |
| `header_title` | Main large heading shown in the page hero banner |
| `header_description` | Short paragraph below the title |
| `header_image` | Custom background photo (replaces Unsplash default) |

**Pages with controllable banners:** `/rooms/`, `/dining/`, `/recreation/`, `/gallery/`, `/conference/`, `/contact/`, `/blogs/`

#### Open Graph Tags
| Field | Description |
|---|---|
| `og_title` | Title when shared on Facebook/LinkedIn |
| `og_description` | Description on social share cards |
| `og_image` | Thumbnail image on social share cards |

#### Twitter Card
| Field | Description |
|---|---|
| `twitter_card` | Card type: summary or summary_large_image |

#### Structured Data
| Field | Description |
|---|---|
| `structured_data` | Raw JSON-LD schema markup for Google rich results |

---

### 17. User Accounts
**Admin path:** `Accounts -> Users`

The admin can view, edit, activate/deactivate, and manage all registered guest and staff accounts. This includes assigning staff permissions and admin access levels.

---

## Guest/User-Submitted Data (Read-Only in Admin)

These records are **created by guests** on the frontend and reviewed by the admin. They cannot be created from admin, but the admin can manage their status:

| Data | Admin Path | What Admin Can Do |
|---|---|---|
| Room Bookings | `Booking -> Bookings` | View details, change status (Pending / Confirmed / Checked In / Checked Out / Cancelled) |
| Payments | `Payments -> Payments` | View gateway, transaction ID, amount, status, raw gateway response (read-only) |
| Dining Reservations | `Dining -> Dining Reservations` | View guest name, venue, date/time, guests; update status (Pending / Confirmed / Cancelled) |
| Conference/Event Inquiries | `Conference -> Event Inquiries` | View guest, venue, event date, catering needs, notes; update status |
| Contact Inquiries | `Contact -> Contact Inquiries` | View name, email, subject, message, category (read-only) |

---

## Static / Hardcoded Content

These items are **built into the code or templates** and cannot be changed from the admin without a developer:

| Item | Location | Notes |
|---|---|---|
| Payment gateways | `payments/models/payment.py` | Stripe, eSewa, Khalti — hardcoded as model choices |
| Recreation category types | `recreation/models/activity.py` | Spa / Pool / Gym / Kids / Casino / Adventure / Safari / Games |
| Dining venue categories | `dining/models/venue.py` | Restaurant / Bar / Cafe / Rooftop / Pool Bar / Fine Dining |
| Booking status flow | `booking/models/booking.py` | Pending / Confirmed / Checked In / Checked Out / Cancelled |
| Hero banner fallback text | All listing templates | Default subtitle/title/description when no SEO record is set |
| Hero banner fallback images | All listing templates | Unsplash photo URLs used when no `header_image` uploaded |
| Footer layout structure | `templates/includes/footer.html` | Number of columns, icon placement — template-level |
| Page URL routing | Each app's `urls.py` | URL patterns like `/rooms/<slug>/` — developer-managed |
| Tax calculation logic | `rooms/models/room.py` | `price_with_tax` property formula |
| Coupon discount logic | `booking/models/coupon.py` | `calculate_discount()` method |
| TailwindCSS design tokens | `static/` and tailwind config | Colour palette, typography, spacing |
| Alpine.js theme logic | `templates/base.html` | Light/Dark/Luxury/Festival theme switching code |
| Currency conversion rates | Not implemented | Prices stored per-currency; no live FX rate conversion |

---

## Summary Table

| Section | Admin Controlled | Guest Submitted | Static / Hardcoded |
|---|:---:|:---:|:---:|
| Hotel name, logos, favicon, admin title & label, theme | YES | | |
| Navigation menus | YES | | |
| Currencies | YES | | |
| Homepage hero slides | YES | | |
| Homepage about section | YES | | |
| Rooms (content, pricing, images) | YES | | |
| Room seasonal prices | YES | | |
| Room policies | YES | | |
| Room facilities list | YES | | |
| Room availability calendar | YES | | |
| Dining venues | YES | | |
| Recreation activities | YES | | |
| Gallery (photos/videos) | YES | | |
| Conference/event venues | YES | | |
| Contact branch offices | YES | | |
| Blog posts | YES | | |
| Nearby attractions | YES | | |
| Guest testimonials | YES | | |
| Discount coupons | YES | | |
| Page SEO & banner text/image | YES | | |
| Social share OG/Twitter tags | YES | | |
| Structured data JSON-LD | YES | | |
| User accounts | YES | | |
| Room bookings | | YES (admin manages status) | |
| Payments | | YES (read-only in admin) | |
| Dining reservations | | YES (admin manages status) | |
| Conference inquiries | | YES (admin manages status) | |
| Contact form messages | | YES (read-only in admin) | |
| Room category types | YES | | |
| Payment gateway options | | | YES |
| Booking status states | | | YES |
| Hero banner fallback defaults | | | YES |
| Page URLs and routing | | | YES |
| UI design and styling | | | YES |
| Tax and discount logic | | | YES |

---

*Generated: July 2026 | Prem Durbar Platform v1.0*
