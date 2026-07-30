# Prem Durbar Hotel & Nagarkot Zipline Platform

A premium, high-performance Django 6 web application and administrative management platform designed for **Prem Durbar Hotel & Nagarkot Zipline** in Nagarkot, Nepal.

---

## 🚀 Key Features & Architectural Enhancements

### 1. Dual Destination & Zipline Booking Engine
* **Streamlined Multi-Currency Engine (`NPR` & `USD`)**: Seamless multi-currency pricing across **Rooms (`RoomBasePrice`)**, **Dining Items (`DiningItemBasePrice`)**, **Zipline Packages (`ZiplinePackageBasePrice`)**, and **Coupons (`CouponMinSpend`)** in **NPR (Nepalese Rupee)** and **USD (US Dollar)**.
* **Homepage Dual Auto-Swiping Carousels**: Simultaneous 4-second auto-swiping sliders for both the **Hotel Sanctuary (Left Column)** and **Nagarkot Zipline Package Cards (Right Column)**, equipped with native passive touch-swipe handlers (`@touchstart.passive` / `@touchend.passive`) for effortless mobile swiping.
* **Interactive Zipline Booking Popup**: Modal sheet featuring live per-flight ticket calculations (`per_person_rate`), body scroll locking, mobile drag-handle pill, safe area insets, real-time client-side Alpine.js validation, and server-side Django input checks.
* **Smart Check-In & Check-Out Pre-filling**: Automatic pass-through of search dates entered on `home.html` to `room_list.html` and `room_detail.html` forms. Intelligently clears session state when visiting home or room list without search parameters so blank forms start cleanly without stale dates.
* **Adaptive Single/Multi-Package Layouts**:
  * **Single Package Mode**: Automatically pairs the single Zipline Package Card and the Live Action Video Preview side-by-side on the exact same row (`grid-cols-1 lg:grid-cols-12`).
  * **Multi-Package Mode**: Expands seamlessly to a 2 or 3-column responsive package grid.
* **High-Contrast Flight Category Badges**: High-contrast, legible category badges (`bg-amber-400 text-neutral-950 font-extrabold shadow-sm`) for flight types (*Classic Seated Harness*, *Superman Flying Harness*, *Tandem Dual Flight*) across both light and dark themes.

### 2. Mobile Responsiveness & Datepicker Ergonomics
* **Mobile-First Touch & Typography**: Responsive title and heading scaling across `home.html`, `zipline.html`, `sustainability.html`, `contact.html`, `checkout.html`, and `footer.html`.
* **AirDatepicker Mobile Keyboard Prevention**: Inputs configured with `readOnly = true` and `inputmode = "none"`, preventing OS virtual keyboards from popping up over datepickers on touch devices.
* **Viewport Overflow Protection**: Dynamic `position()` boundary clamping ensuring datepickers never exceed viewport bounds or trigger horizontal scrolling (`overflow-x`).

### 3. Modularized Booking Architecture
* **Domain-Driven View Modules (`booking/views/`)**:
  * `booking/views/zipline.py`: Zipline flight creation, coupon discounts, and input validation.
  * `booking/views/rooms.py`: Room chamber reservations, seasonal rate overrides, and availability checks.
  * `booking/views/checkout.py`: Unified guest checkout and payment gateway initiation.
  * `booking/views/api.py`: OTA channel manager synchronization hooks.

### 4. Administrative Workflows & Dashboard Balancing
* **Balanced 4/4 Top Metrics Grid**:
  * **Row 1**: Today's Revenue, Occupancy Rate, Check-ins Today, Check-outs Today.
  * **Row 2**: Confirmed Bookings, Pending Bookings, Contact Messages Today, Zipline Flights Today.
* **Domain-Aware Administrative Workflows**: Customized status workflows and action buttons tailored for **Zipline Flights** (*Ticket Redeemed*, *Flight Completed*) versus **Room Chambers** (*Checked In*, *Checked Out*).
* **Confirmed Payment Exclusions**: Excludes abandoned `draft` bookings from daily operational metrics and check-in/out counts.
* **Zipline Package Formset Editor**: Dedicated admin editor (`admin_dashboard/zipline/package_form.html`) for package specifications, publication status toggling, and inline multi-currency price formsets.

---

## 🛠️ Tech Stack

* **Backend**: Django 6.0, Python 3.14
* **Frontend**: Vanilla CSS, TailwindCSS, Alpine.js, FontAwesome 6 Icons
* **Database**: SQLite (default local) / PostgreSQL 15 (Docker)
* **Caching & Queue**: Redis 7, Celery 5
* **Package Manager**: `uv`

---

## ⚙️ Quick Start & Installation

### Option A: Using Docker Compose (Recommended for Production Stack)
```bash
# 1. Start all containers (PostgreSQL, Redis, Web App, Celery Worker)
docker-compose up -d --build

# 2. Access Web App on http://localhost:8000/
```

### Option B: Local Development with `uv`
```bash
# 1. Sync virtual environment and install dependencies
uv sync

# 2. Run database migrations
uv run python manage.py migrate

# 3. Seed Prem Durbar hotel settings, room suites, zipline packages, and CMS data
uv run python manage.py seed_data

# 4. Start local development server
uv run python manage.py runserver 0.0.0.0:8000
```
Visit the homepage at `http://127.0.0.1:8000/` and the custom admin portal at `http://127.0.0.1:8000/admin-dashboard/`.

---

## 📁 Key Repository Structure

```text
├── admin_dashboard/           # Custom Admin Portal & Manager Views
│   ├── templates/admin_dashboard/zipline/  # Zipline dashboard & package formset editor
│   └── views/zipline.py       # Zipline package CMS & multi-currency price view
├── booking/                   # Modular Booking Engine
│   ├── views/                 # Modular Domain Views
│   │   ├── zipline.py         # Zipline flight creation & multi-currency rates
│   │   ├── rooms.py           # Room chamber reservations & availability
│   │   ├── checkout.py        # Guest checkout & payment summary
│   │   └── api.py             # Channel manager OTA sync
│   └── models/booking.py      # Booking model helper properties (status_label, per_person_rate)
├── homepage/                  # Public Homepage & Adventure Listings
│   ├── models/zipline_package.py # ZiplinePackage & ZiplinePackageBasePrice models
│   └── templates/homepage/    # Homepage, Zipline page & Zipline booking modal
├── core/records/              # YAML Data Seeder Files (USD & NPR Currencies)
└── payments/                  # Multi-Currency Payment Callbacks & Stripe/eSewa/Khalti
```

---

## 🖼️ Dynamic Page Banners & CMS

| Page | URL Path | CMS Control Tab |
|---|---|---|
| Rooms & Accommodation | `/rooms/` | SEO Meta tags / Rooms Manager |
| Gastronomy & Dining | `/dining/` | SEO Meta tags / Dining Items |
| About Us & Heritage | `/about/` | About Us Page CMS |
| Zipline Adventure | `/zipline/` | Zipline CMS & Video / Zipline Packages |
| Sustainability & Eco | `/sustainability/` | Sustainability CMS |
| Resort Photo Gallery | `/gallery/` | Gallery Bulk |
| Concierge & Contact | `/contact/` | Contact Branches |
