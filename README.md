# Prem Durbar Hotel & Nagarkot Zipline Platform

A premium, high-performance Django 6 web application and administrative management platform designed for **Prem Durbar Hotel & Nagarkot Zipline** in Nagarkot, Nepal.

---

## 🚀 Key Features & Architectural Enhancements

### 1. Dual Destination & Zipline Booking Engine
* **Multicurrency Zipline Pricing (`ZiplinePackageBasePrice`)**: Complete multi-currency support across **Rooms (`RoomBasePrice`)**, **Dining Food Items (`DiningItemBasePrice`)**, and **Zipline Packages (`ZiplinePackageBasePrice`)** in NPR, USD, EUR, GBP, and INR.
* **Homepage Dual Auto-Swiping Carousels**: Simultaneous 4-second auto-swiping sliders for both the **Hotel Sanctuary (Left Column)** and **Nagarkot Zipline Package Cards (Right Column)**, complete with manual controls and direct booking triggers.
* **Interactive Zipline Booking Popup**: Modal popup featuring live per-flight ticket calculations (`per_person_rate`), date selection limits (preventing past date selection), body scroll locking, real-time client-side Alpine.js validation, and server-side Django input checks.
* **Adaptive Single/Multi-Package Layouts**:
  * **Single Package Mode**: Automatically pairs the single Zipline Package Card and the Live Action Video Preview side-by-side on the exact same row (`grid-cols-1 lg:grid-cols-12`).
  * **Multi-Package Mode**: Expands seamlessly to a 2 or 3-column responsive package grid.
* **High-Contrast Flight Category Badges**: Bright, legible category badges (`bg-amber-400 text-neutral-950 font-extrabold`) for flight types (*Classic Seated Harness*, *Superman Flying Harness*, *Tandem Dual Flight*) across light and dark themes.

### 2. Modularized Booking Architecture
* **Domain-Driven View Modules (`booking/views/`)**:
  * `booking/views/zipline.py`: Zipline flight creation, coupon discounts, and input validation.
  * `booking/views/rooms.py`: Room chamber reservations, seasonal rate overrides, and availability checks.
  * `booking/views/checkout.py`: Unified guest checkout and payment gateway initiation.
  * `booking/views/api.py`: OTA channel manager synchronization hooks.

### 3. Administrative Workflows & Dashboard Balancing
* **Balanced 4/4 Top Metrics Grid**:
  * **Row 1**: Today's Revenue, Occupancy Rate, Check-ins Today, Check-outs Today.
  * **Row 2**: Confirmed Bookings, Pending Bookings, Contact Messages Today, Zipline Flights Today.
* **Domain-Aware Administrative Workflows**: Customized status workflows and action buttons tailored for **Zipline Flights** (*Ticket Redeemed*, *Flight Completed*) versus **Room Chambers** (*Checked In*, *Checked Out*).
* **Confirmed Payment Exclusions**: Excludes abandoned `draft` bookings from daily operational metrics and check-in/out counts.
* **Zipline Package Formset Editor**: Dedicated admin editor (`admin_dashboard/zipline/package_form.html`) for package specifications, publication status toggling, and inline multi-currency price formsets.

### 4. Resort & Guest Experience Polish
* **Rooms & Suites Category Display**: Displays exact category names (`room.category.name`) on card image badges and inline detail headers across the homepage.
* **Dynamic Theme System**: Dynamic theme-aware layout styling supporting Light, Dark, Luxury Gold, and Festival modes without client-side render flickering.
* **Standardized Invoicing Engine**: Unified, print-ready layout (`invoice.html`) showing dynamic hotel header branding, itemized room unit/night tallies, clear payment status tags, and visual callouts.

---

## 🛠️ Tech Stack

* **Backend**: Django 6.0, Python 3.14
* **Frontend**: Vanilla CSS, TailwindCSS, Alpine.js, FontAwesome 6 Icons
* **Database**: SQLite (default local) / PostgreSQL support
* **Package Manager**: `uv`

---

## ⚙️ Quick Start & Installation

### Option A: Using Makefile (Recommended)
```bash
# 1. Complete one-step setup (installs environment, runs migrations, and seeds data)
make setup

# 2. Start local development server (binds on 0.0.0.0:8000)
make run

# 3. Collect static files into staticfiles directory
make collectstatic

# 4. Run system checks and test suite
make test
```

### Option B: Manual Setup
```bash
# 1. Sync virtual environment and install dependencies
uv sync

# 2. Run database migrations
uv run python manage.py migrate

# 3. Seed Prem Durbar hotel settings, room suites, zipline packages, and CMS data
uv run python manage.py seed_data --update

# 4. Start development server
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
