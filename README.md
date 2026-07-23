# Prem Durbar Hotel & Nagarkot Zipline Platform

A premium, high-performance Django-based hospitality, gastronomy, and adventure management platform designed for Prem Durbar Hotel & Nagarkot Zipline in Nagarkot, Nepal.

---

## 🚀 Key Features

*   **Multi-Currency Pricing Architecture**: Comprehensive multi-currency pricing across both **Rooms (`RoomBasePrice`)** and **Dining Food Items (`DiningItemBasePrice`)**. Staff can specify base rates per currency (NPR, USD, EUR, GBP, INR) with mandatory currency validation in the Admin Panel.
*   **Real-Time Currency Switcher**: Server-side cookie-driven currency selector (desktop navigation bar dropdown & mobile native selector). Prices across room suites and food dishes update instantly to the guest's selected currency.
*   **Full White-Label & Dynamic Branding**: Dynamic hotel site identity managed directly from the Admin Panel — including Site Name, Light & Dark Logos, Admin Dashboard Logo, Browser Favicon (.png, .ico, .svg), Admin Tab Title, Admin Sidebar Label, Footer Story, and Contact Details.
*   **Dedicated Page Content CMS**: Complete CMS control tabs in `/admin-dashboard/` (`CMS Content`) for:
    *   **About Us Page (`AboutCMS`)**: Hero banners, valley artistry story headers, story body text, and promo tour video links.
    *   **About Preview (Homepage) (`AboutPreview`)**: Homepage `/` intro text, illustration photos, video link, and 4 statistical counters (Chambers, Longest Zipline, 100% Organic, 5k+ Adventurers).
    *   **Zipline Adventure Page (`ZiplineCMS`)**: Hero banner, specifications (Length, Speed, Elevation, Safety Certification), overview text, and a **Live Action Video Preview Player** (supporting MP4 file uploads & YouTube/Vimeo embeds).
    *   **Sustainability Page (`SustainabilityCMS` & `SustainabilityPillar`)**: Environmental & community pillar cards with icon, title, description, and ordering.
*   **Pure F&B Food Menu Showcase (`DiningItem`)**: Renamed and streamlined Dining section presenting 101 food menu items with dietary badges (Veg, Vegan, Spicy, Chef Special), category filtering, and live multi-currency pricing.
*   **Air Datepicker & File Upload Widgets**: Modern date inputs with Air Datepicker UI and a custom file uploader widget with live thumbnail image previews and one-click remove buttons.
*   **Standardized Invoicing Engine**: Unified, print-ready layout (`invoice.html`) showing dynamic hotel header branding, itemized room unit/night tallies, clear payment status tags, and visual callouts.
*   **Dynamic Theme System**: Dynamic theme-aware layout styling supporting Light, Dark, Luxury Gold, and Festival modes without client-side render flickering.
*   **Custom Admin Dashboard**: Administrative portal (`/admin-dashboard/`) featuring check-ins/check-outs, occupancy analytics, dynamic 7-day charts, multi-currency revenue tracking, recent activity logs, and manager tabs.
*   **Responsive Booking Engine**: Full room reservation flow with dynamic calculation, checkout pages, and payment gateway integrations (Stripe, eSewa, Khalti).
*   **Optimized Performance**: Packaged with `uv` for lightning-fast Python dependency management and compilation.

---

## 🛠️ Tech Stack

*   **Backend**: Django 6, Python 3.14
*   **Frontend**: Vanilla CSS, TailwindCSS, Alpine.js, FontAwesome Icons
*   **Database**: SQLite (default local) / PostgreSQL support
*   **Package Manager**: `uv`

---

## ⚙️ Quick Start & Installation

### Option A: Using Makefile (Recommended)
If you have `make` installed on your system, execute:
```bash
# 1. Complete one-step setup (installs environment, runs migrations, and seeds data)
make setup

# 2. Start local development server (binds on 0.0.0.0:8000)
make run

# 3. Collect static files into staticfiles directory
make collectstatic

# 4. Run the automated test suite
make test
```

### Option B: Manual Setup
If `make` is not available, execute the manual setup commands:

```bash
# 1. Sync virtual environment and install dependencies
uv sync

# 2. Run database migrations
uv run python manage.py migrate

# 3. Seed Prem Durbar hotel settings, room suites, multi-currency rates, food menu, and CMS data
uv run python manage.py seed_data --update

# 4. Start development server
uv run python manage.py runserver 0.0.0.0:8000
```
Visit the homepage at `http://127.0.0.1:8000/` and the custom admin portal at `http://127.0.0.1:8000/admin-dashboard/`.

---

## 📁 Repository Structure & Data Loading

*   `seed_data.yaml`: Stores essential currencies (NPR, USD, EUR, GBP, INR), hotel settings, room categories, food dishes, CMS content for About/Zipline/Sustainability, and branch details.
*   `core/management/commands/seed_data.py`: Main database seeding command.
*   `templates/base.html`: Core base template containing dynamic navigation headers, currency selector, theme toggles, and mobile menus.

---

## 💾 Database Backup & Cronjob Setup

The project includes an automatic database backup command supporting SQLite and PostgreSQL. It creates timestamped backup files under `backups/`:

### Manual Execution
```bash
uv run python manage.py db_backup --keep 10
```

### Automation via Cronjob
Run daily at 2:00 AM:
```text
0 2 * * * /home/user/Workflow/Hotel\ Platform/Prem-Durbar-Zipline/scripts/backup.sh
```

---

## 🖼️ Dynamic Page Banners (SEO Admin)

Every major listing page has a **customizable hero banner** (subtitle, title, description, and background image) managed directly from the Admin Panel.

### Pages with Dynamic Banners & CMS

| Page | URL Path | CMS Control Tab |
|---|---|---|
| Rooms & Accommodation | `/rooms/` | SEO Meta tags / Rooms Manager |
| Gastronomy & Dining | `/dining/` | SEO Meta tags / Dining Items |
| About Us & Heritage | `/about/` | About Us Page CMS |
| Zipline Adventure | `/zipline/` | Zipline CMS & Video |
| Sustainability & Eco | `/sustainability/` | Sustainability CMS |
| Resort Photo Gallery | `/gallery/` | Gallery Bulk |
| Concierge & Contact | `/contact/` | Contact Branches |
