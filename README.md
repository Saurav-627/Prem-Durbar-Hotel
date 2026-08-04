# Prem Durbar Hotel & Nagarkot Zipline Platform

A premium, high-performance Django 6 web application, automated booking engine, real-time payment gateway integration, and administrative management platform built for **Prem Durbar Hotel & Nagarkot Zipline** in Nagarkot, Nepal.

---

## 🚀 Key Features & Architectural Highlights

### 1. Multi-Currency Engine (`NPR` & `USD`)
* **Unified Multi-Currency Pricing**: Seamless multi-currency support across **Rooms (`RoomBasePrice`)**, **Zipline Packages (`ZiplinePackageBasePrice`)**, **Dining Menu Items (`DiningItemBasePrice`)**, and **Coupons (`CouponMinSpend`)** in **NPR (Nepalese Rupee)** and **USD (US Dollar)**.
* **Pricing Precedence Hierarchy**:
  1. 🥇 **Seasonal Price Override** (`active_seasonal`): Applied first during designated high-season/holiday date ranges.
  2. 🥈 **Discounted Price** (`discount_price`): Applied when an offer/sale price is set (must be less than `base_price`).
  3. 🥉 **Base Price** (`base_price`): Standard default rate fallback.
* **Strikethrough Display System**: Visual strikethrough styling for original base rates (~~NPR 4,500.00~~) alongside highlighted active sale/discounted prices (**NPR 3,500.00**) across homepage, room listings, zipline cards, booking modals, and official invoices.

### 2. Dual Destination & Zipline Booking Engine
* **Dual Auto-Swiping Carousels**: Simultaneous 4-second auto-swiping sliders on the homepage for the **Hotel Sanctuary (Left Column)** and **Nagarkot Zipline Package Cards (Right Column)**, equipped with passive touch-swipe handlers (`@touchstart.passive` / `@touchend.passive`).
* **Interactive Zipline Booking Modal**: Popup drawer featuring live per-flight ticket calculations, body scroll locking, mobile drag-handle pill, safe area insets, Alpine.js reactive validation, and server-side Django checks.
* **Smart Check-In/Check-Out Date Pre-filling**: Automatic pass-through of search dates entered on `home.html` to `room_list.html` and `room_detail.html`. Session state resets when navigating without parameters to prevent stale date conflicts.
* **Context-Aware Reservation Success Pages**: Tailored confirmation screens for Zipline Bookings (*"Zipline Flight Confirmed"* / flight details) vs Room Stays (*"Reservation Confirmed"* / room suite details).

### 3. Real Stripe Payment Integration & Webhook System
* **Stripe Checkout Service (`payments/services/stripe_payment.py`)**: Real Stripe Checkout Session generation with line items, multi-currency conversion, success/cancel redirects, and guest metadata.
* **Stripe SDK v15+ Compatibility**: Robust object dictionary conversion using `session.to_dict()` to prevent `KeyError: 0` and `AttributeError: get` errors.
* **Stripe Webhook API (`/payments/webhook/stripe/`)**: Handles `checkout.session.completed` events. Atomically updates payment status to `success` and marks reservations as `confirmed`.
* **Local Webhook Development Helper**: `make stripe-listen` CLI shortcut using Stripe CLI forwarding to `127.0.0.1:8000`.

### 4. Detailed Financial Breakdown & Invoice Engine
* **Checkout Summary Breakdown (`booking/templates/booking/checkout.html`)**: Displays Subtotal, Saved Discount, Tax with percentage e.g. `Tax (13%)` (when `tax > 0`), and Estimated Total (incl. tax).
* **Official PDF/Print Invoices (`admin_dashboard/templates/admin_dashboard/bookings/invoice.html`)**:
  * Displays itemized rate line items, currency symbols, tax amounts, and payment transaction logs.
  * Displays status badges for both **Seasonal Price Overrides** (`🏷️ Seasonal Price: <Season Name>`) and **Discount Offers** (`🏷️ Special Offer Discount`).

### 5. Mobile Ergonomics & UX Improvements
* **AirDatepicker Mobile Keyboard Prevention**: Inputs configured with `readOnly = true` and `inputmode = "none"`, preventing virtual keyboards from popping up on mobile touch devices.
* **Dynamic Viewport Boundary Clamping**: Boundary positioning clamping to keep datepicker popups within viewport bounds without horizontal scrolling (`overflow-x`).
* **Optional Room Highlights**: `Room.highlights` field made optional (`blank=True, null=True`) for flexible room listing creation.

### 6. Administrative Dashboard & Workflows
* **Balanced 4/4 Analytics Metric Grid**:
  * **Row 1**: Today's Revenue, Occupancy Rate, Check-ins Today, Check-outs Today.
  * **Row 2**: Confirmed Bookings, Pending Bookings, Contact Messages Today, Zipline Flights Today.
* **Domain-Aware Action Workflows**: Tailored status workflows for **Zipline Flights** (*Ticket Redeemed*, *Flight Completed*) versus **Room Chambers** (*Checked In*, *Checked Out*).
* **Clear Form Field Labels**: Form fields in Admin UI explicitly labeled as **"Base Price (Regular Rate)"** and **"Discounted Price (Sale Price) (Optional)"**.
* **Standardized Seed Importer**: `uv run python manage.py seed_data --update` imports data across 21 YAML files with progress summary logs (`Processed X: A created, B updated, C skipped`).

---

## 🛠️ Tech Stack

* **Backend**: Django 6.0, Python 3.14
* **Frontend**: Vanilla HTML/JS, Vanilla CSS, TailwindCSS, Alpine.js, FontAwesome 6
* **Database**: SQLite (local development) / PostgreSQL 15 (production / Docker)
* **Caching & Async Queue**: Redis 7, Celery 5
* **Payment Gateways**: Stripe (Checkout & Webhooks), eSewa, Khalti
* **Package & Task Runner**: `uv`, `make`

---

## ⚙️ Quick Start & Environment Setup

### 1. Prerequisites
Ensure `uv` and Python 3.14+ are installed.

### 2. Environment Variables Configuration (`.env`)
Create a `.env` file in the project root:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Stripe Credentials
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Local Installation Steps
```bash
# 1. Sync dependencies and setup virtualenv
uv sync

# 2. Apply database migrations
uv run python manage.py migrate

# 3. Seed initial database data (hotel settings, suites, zipline packages, coupons)
uv run python manage.py seed_data --update

# 4. Run local server
make run
# or: uv run python manage.py runserver 0.0.0.0:8000
```

### 4. Running Local Stripe Webhook Listener
In a separate terminal window:
```bash
make stripe-listen
```

### 5. Accessing Application Portals
* **Public Website**: `http://127.0.0.1:8000/`
* **Admin Panel**: `http://127.0.0.1:8000/admin/`

---

## 📁 Repository Directory Architecture

```text
├── admin_dashboard/           # Custom Management Dashboard
│   ├── forms.py               # Customized forms (RoomBasePriceForm, ZiplinePackageBasePriceForm)
│   ├── templates/admin_dashboard/
│   │   ├── bookings/invoice.html # PDF/Print Official Invoice Template
│   │   ├── rooms/form.html    # Multi-currency room price formset
│   │   └── zipline/package_form.html # Zipline package formset editor
│   └── views/                 # Dashboard views for rooms, zipline, bookings, coupons
├── booking/                   # Modular Booking Engine
│   ├── models/booking.py      # Booking model & pricing breakdown fields
│   ├── templates/booking/
│   │   └── checkout.html      # Detailed financial breakdown & gateway selection
│   └── views/
│       ├── rooms.py           # Room booking logic & availability validation
│       ├── zipline.py         # Zipline booking logic & flight date check
│       └── checkout.py        # Checkout view & tax recalculation
├── core/
│   ├── management/commands/
│   │   └── seed_data.py       # YAML Data importer with summary logging
│   └── records/               # 21 YAML seed records (hotel, rooms, zipline, coupons)
├── homepage/                  # Public Website & Adventure Pages
│   ├── models/zipline_package.py # ZiplinePackage & ZiplinePackageBasePrice models
│   └── templates/homepage/    # Homepage, zipline page, and booking modal
├── payments/                  # Multi-Currency Payment Integrations
│   ├── services/
│   │   ├── stripe_payment.py  # Stripe Checkout Session builder
│   │   ├── esewa_payment.py   # eSewa payment gateway service
│   │   └── khalti_payment.py  # Khalti payment gateway service
│   ├── templates/payments/
│   │   └── success.html       # Dynamic context-aware booking success page
│   └── views/public.py        # Payment process & Stripe Webhook API endpoint
├── rooms/                     # Hotel Room Chambers Domain
│   ├── models/                # Room, RoomCategory, RoomFacility, RoomBasePrice, RoomSeasonalPrice
│   └── templates/rooms/       # Room list & detail templates with live price calculator
└── Makefile                   # Command shortcuts (make run, make stripe-listen)
```

---

## 🖼️ Dynamic Page Routes & CMS Map

| Page | Path | CMS Management Tab | Description |
|---|---|---|---|
| Homepage | `/` | Hero Slides, About Preview, Zipline CMS | Hero slider, suites showcase, zipline section |
| Rooms & Suites | `/rooms/` | Rooms Manager | Multi-currency room suites, seasonal rates, facility checklists |
| Room Detail | `/rooms/<slug>/` | Rooms Manager | Live price calculator widget, virtual tours, room policies |
| Zipline Packages | `/zipline/` | Zipline Manager | Zipline package cards, flight preview video, flight booking modal |
| Gastronomy | `/dining/` | Dining Items | Multi-currency food & beverage menu |
| About Us | `/about/` | About CMS & Team | Hotel story, executive management team |
| Sustainability | `/sustainability/` | Sustainability CMS | Eco-initiatives & sustainability pillars |
| Photo Gallery | `/gallery/` | Gallery Bulk | Photo gallery categories & image uploads |
| Contact Us | `/contact/` | Contact Branches | Branch offices, inquiries, Google Maps embed |
| Guest Checkout | `/booking/checkout/<uid>/` | Booking Manager | Financial breakdown (Subtotal, Tax, Discount, Total) & payment choice |
| Stripe Webhook | `/payments/webhook/stripe/` | Payment Manager | Automated Stripe webhook event processor |
| Print Invoice | `/payments/invoice/<uid>/` | Booking Manager | Official printable receipt / PDF invoice |

---

## 🔒 Pricing Validation & Safeguards

- **Discount Price Validation**: Enforces `discount_price < base_price`. If an admin enters `discount_price >= base_price`, the form rejects the submission with a clear error message, and model properties return `None` to prevent invalid strikethroughs.
- **Atomic Webhook Operations**: Stripe webhooks run inside `@transaction.atomic` blocks to prevent race conditions during payment completion.
- **Tax Precision**: Tax calculations use Django `Decimal` precision quantization (`Decimal('0.01')`) for exact currency alignment across NPR and USD.
