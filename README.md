# Prem Durbar Platform

A premium, high-performance Django-based hospitality and booking management platform designed for luxury hotels and resorts.

---

## 🚀 Key Features

*   **Full White-Label & Dynamic Branding**: Completely dynamic hotel site identity managed from the Admin Panel — including Site Name, Light & Dark Logos, Admin Dashboard Logo, Browser Favicon (.png, .ico, .svg), Admin Tab Title, Admin Sidebar Label, Footer Story, and Contact Details.
*   **Server-Side Currency Persistence**: Persistent cookie-driven currency switcher (desktop dropdown, mobile sidebar native select) that filters room listings and payment flows dynamically.
*   **Renamed Multi-Currency Pricing Schema**: Clear, logical database modeling using `RoomBasePrice` (standard nightly rates per currency) and `RoomSeasonalPrice` (temporary seasonal overrides with optional currency-specific restrictions or wildcards).
*   **Air Datepicker & Enhanced File Upload Widgets**: Modern `type="date"` inputs with Air Datepicker UI and a custom file uploader widget with live thumbnail image previews and one-click remove buttons.
*   **Standardized Invoicing Engine**: Guest-facing and staff-facing views use the same unified, print-ready layout (`invoice.html`) showing dynamic hotel header branding, itemized room unit/night tallies, clear payment status tags, and visual callouts.
*   **Overlapping Seasonal Rules**: High-fidelity date overlap calculations during checkout ensures the guest gets their promotional rate for any night of their stay, prioritizing specific currency overrides over wildcard ones.
*   **Dynamic Theme System**: Dynamic theme-aware layout styling supporting Light, Dark, Luxury Gold, and Festival modes without client-side render flickering.
*   **Custom Admin Dashboard**: Custom-branded administrative dashboard (`/admin/`) featuring check-ins/check-outs, occupancy analytics, dynamic 7-day charts, recent activity logs, and dedicated **Settings Manager** and **Payment Processors** CRUD manager tabs.
*   **Multi-Currency Revenue Tracking**: Auto-grouped dashboard revenue statistics today/monthly and daily trend charts categorizing transactions by currency code (e.g. NPR, USD).
*   **Correct Booking Currency Rendering**: Booking list and details views display the exact currency code used at booking registration rather than defaulting to the base room currency code.
*   **Responsive Booking Engine**: Full booking initiation flow complete with a dynamic reservation calculator, checkout page, and gateway integrations (Stripe, eSewa, Khalti).
*   **Optimized Performance**: Packaged with `uv` for lightning-fast Python dependency management and compilation.

---

## 🛠️ Tech Stack

*   **Backend**: Django 6, Python 3.14
*   **Frontend**: TailwindCSS, Alpine.js, FontAwesome Icons
*   **Database**: SQLite (default local) / PostgreSQL support
*   **Package Manager**: `uv`

---

## ⚙️ Quick Start & Installation

### Option A: Using Makefile (Recommended)
If you have `make` installed on your system, you can use the single-step helper targets:
```bash
# 1. Complete one-step setup (installs environment, runs migrations, and seeds data)
make setup

# 2. Start local development server (binds on all interfaces)
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

# 2. Run the migrations to create the database schema
uv run python manage.py migrate

# 3. Load currencies, settings, and navigation layout
uv run python manage.py import_initial_data

# 4. Import room categories, dining venues, attractions, and test data
uv run python manage.py seed_all

# 5. Create administrative user
uv run python manage.py createsuperuser

# 6. Start development server
uv run python manage.py runserver
```
Visit the homepage at `http://127.0.0.1:8000/` and the custom admin portal at `http://127.0.0.1:8000/admin/`.

---

## 📁 Repository Structure & Data Loading

*   `initial_data.yaml`: Stores essential currencies (USD, NPR, EUR, GBP), header navigation paths, and initial branding metadata.
*   `settings_manager/`: Contains models for Currency, Navigation menus, and Global Hotel Settings, along with the command line import utilities.
*   `templates/base.html`: Core base template containing dynamic navigation headers, mobile responsive menus, and general assets.

---

## 💾 Database Backup & Cronjob Setup

The project includes an automatic database backup command supporting both SQLite and PostgreSQL. It automatically creates backup files under `backups/` and keeps only the most recent backups to prevent the disk from filling up.

### Manual Execution
To create a backup and keep the last 10 backups:
```bash
uv run python manage.py db_backup --keep 10
```

### Automation via Cronjob
A helper shell script `scripts/backup.sh` is provided in the repository root. To schedule backups daily at 2:00 AM:

1. Open your system's crontab editor:
   ```bash
   crontab -e
   ```
2. Add the following entry (updating the directory path to your project's absolute path):
   ```text
   0 2 * * * /home/user/Workflow/Hotel\ Platform/Hotel-Ichchha/scripts/backup.sh
   ```

---

## 🖼️ Dynamic Page Banners (SEO Admin)

Every major listing page has a **fully customizable hero banner** (subtitle, title, description, and background image) that can be managed directly from the Django Admin portal — no code changes required.

### How It Works

Each page banner is driven by the `SEOData` model (`seo` app). A **context processor** runs on every request, looks up the database for a record matching the current URL path, and exposes it as `seo_raw` to all templates.

- If a matching record **exists** → the page renders the admin-configured values.
- If no record **exists** → the page falls back to built-in default text and a default Unsplash image.

### Pages with Dynamic Banners

| Page | URL Path to configure |
|---|---|
| Rooms & Accommodation | `/rooms/` |
| Gastronomy & Dining | `/dining/` |
| Recreation & Wellness | `/recreation/` |
| Resort Photo Gallery | `/gallery/` |
| Conferences & Venues | `/conference/` |
| Concierge & Contact | `/contact/` |
| News & Blog | `/blogs/` |

### Configuring a Banner from Admin

1. Go to **`/admin/`** → **SEO → SEO Page Data** → click **"+ Add SEO Page Data"**
2. Fill in the **🔗 Page Identity** section:
   - `Path` — must match exactly, e.g. `/rooms/` (include trailing slash)
   - `Meta Title` and `Meta Description` — for browser tab and search results
3. Fill in the **🖼️ Banner Header** section:
   - `Header Subtitle` — small uppercase label above the title (e.g. *"Sanctuary Suites"*)
   - `Header Title` — main large heading (e.g. *"Rooms & Accommodation"*)
   - `Header Description` — short paragraph below the title
   - `Header Image` — upload a custom background photo (max 2 MB); replaces the default Unsplash image
4. **Save** — changes appear immediately on the live page.

> **Tip:** Leave any Banner Header field blank to keep the page's built-in default for that field.

### Architecture Reference

| File | Role |
|---|---|
| `seo/models/seo_data.py` | `SEOData` model with `header_subtitle`, `header_title`, `header_description`, `header_image` fields |
| `seo/context_processors.py` | Injects `seo_raw` (the matched `SEOData` instance) into every template context |
| `seo/admin.py` | Registered admin with labelled fieldsets for easy banner editing |
| `*/templates/*_list.html` | Each template uses `{{ seo_raw.header_title\|default:"..." }}` with fallbacks |
