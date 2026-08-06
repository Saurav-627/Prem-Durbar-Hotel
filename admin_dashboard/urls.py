from django.urls import path

from .views import (
    auth,
    bookings,
    cms,
    contact,
    coupons,
    dining,
    home,
    notifications,
    payments,
    rooms,
    settings,
    users,
    zipline,
)

app_name = 'admin_dashboard'

urlpatterns = [
    # Auth
    path('login/', auth.DashboardLoginView.as_view(), name='login'),
    path('logout/', auth.DashboardLogoutView.as_view(), name='logout'),
    
    # Dashboard Home
    path('', home.DashboardHomeView.as_view(), name='home'),

    # Notifications
    path('notifications/', notifications.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/read/', notifications.mark_notification_read, name='notification_mark_read'),
    path('notifications/read-all/', notifications.mark_all_notifications_read, name='notification_mark_all_read'),
    
    # Bookings
    path('bookings/', bookings.BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/', bookings.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/update-status/', bookings.BookingUpdateStatusView.as_view(), name='booking_update_status'),
    path('bookings/<int:pk>/invoice/', bookings.BookingInvoiceView.as_view(), name='booking_invoice'),

    # Promo & Coupon Manager
    path('coupons/', coupons.CouponDashboardView.as_view(), name='coupon_dashboard'),
    path('coupons/add/', coupons.CouponCreateView.as_view(), name='coupon_create'),
    path('coupons/<int:pk>/edit/', coupons.CouponUpdateView.as_view(), name='coupon_edit'),
    path('coupons/<int:pk>/delete/', coupons.CouponDeleteView.as_view(), name='coupon_delete'),
    
    # Rooms
    path('rooms/', rooms.RoomDashboardView.as_view(), name='room_dashboard'),
    path('rooms/add/', rooms.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:pk>/edit/', rooms.RoomUpdateView.as_view(), name='room_edit'),
    path('rooms/<int:pk>/delete/', rooms.RoomDeleteView.as_view(), name='room_delete'),
    
    path('rooms/category/add/', rooms.RoomCategoryCreateView.as_view(), name='room_category_create'),
    path('rooms/category/<int:pk>/edit/', rooms.RoomCategoryUpdateView.as_view(), name='room_category_edit'),
    path('rooms/category/<int:pk>/delete/', rooms.RoomCategoryDeleteView.as_view(), name='room_category_delete'),
    
    path('rooms/facility/add/', rooms.RoomFacilityCreateView.as_view(), name='room_facility_create'),
    path('rooms/facility/<int:pk>/edit/', rooms.RoomFacilityUpdateView.as_view(), name='room_facility_edit'),
    path('rooms/facility/<int:pk>/delete/', rooms.RoomFacilityDeleteView.as_view(), name='room_facility_delete'),
    
    path('rooms/price/add/', rooms.RoomSeasonalPriceCreateView.as_view(), name='room_seasonal_price_create'),
    path('rooms/price/<int:pk>/edit/', rooms.RoomSeasonalPriceUpdateView.as_view(), name='room_seasonal_price_edit'),
    path('rooms/price/<int:pk>/delete/', rooms.RoomSeasonalPriceDeleteView.as_view(), name='room_seasonal_price_delete'),
    
    path('rooms/availability/', rooms.RoomAvailabilityCalendarView.as_view(), name='room_availability_calendar'),
    path('rooms/bulk-price/', rooms.RoomBulkPriceUpdateView.as_view(), name='room_bulk_price'),
    path('rooms/bulk-publish/', rooms.RoomBulkPublishView.as_view(), name='room_bulk_publish'),
    
    # Payments
    path('payments/', payments.PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', payments.PaymentDetailView.as_view(), name='payment_detail'),
    
    # Dining
    path('dining/', dining.DiningDashboardView.as_view(), name='dining_dashboard'),
    path('dining/item/add/', dining.DiningItemCreateView.as_view(), name='dining_item_create'),
    path('dining/item/<int:pk>/edit/', dining.DiningItemUpdateView.as_view(), name='dining_item_edit'),
    path('dining/item/<int:pk>/delete/', dining.DiningItemDeleteView.as_view(), name='dining_item_delete'),

    # Ziplines Management
    path('zipline/', zipline.ZiplineDashboardView.as_view(), name='zipline_dashboard'),
    path('zipline/cms/', zipline.ZiplineCMSUpdateView.as_view(), name='zipline_cms_update'),
    path('zipline/package/add/', zipline.ZiplinePackageCreateView.as_view(), name='zipline_package_create'),
    path('zipline/package/<int:pk>/edit/', zipline.ZiplinePackageUpdateView.as_view(), name='zipline_package_edit'),
    path('zipline/package/<int:pk>/delete/', zipline.ZiplinePackageDeleteView.as_view(), name='zipline_package_delete'),
    
    # Contact & Newsletter
    path('contact/', contact.ContactDashboardView.as_view(), name='contact_dashboard'),
    path('contact/branch/add/', contact.BranchCreateView.as_view(), name='branch_create'),
    path('contact/branch/<int:pk>/edit/', contact.BranchUpdateView.as_view(), name='branch_edit'),
    path('contact/branch/<int:pk>/delete/', contact.BranchDeleteView.as_view(), name='branch_delete'),
    path('contact/category/add/', contact.ContactInquiryCategoryCreateView.as_view(), name='category_create'),
    path('contact/category/<int:pk>/edit/', contact.ContactInquiryCategoryUpdateView.as_view(), name='category_edit'),
    path('contact/category/<int:pk>/delete/', contact.ContactInquiryCategoryDeleteView.as_view(), name='category_delete'),
    path('contact/inquiry/<int:pk>/', contact.ContactInquiryDetailView.as_view(), name='contact_inquiry_detail'),
    path('contact/newsletter/broadcast/', contact.BroadcastNewsletterView.as_view(), name='newsletter_broadcast'),
    path('contact/newsletter/<int:pk>/toggle-status/', contact.NewsletterSubscriberToggleStatusView.as_view(), name='newsletter_toggle_status'),
    path('contact/newsletter/<int:pk>/delete/', contact.NewsletterSubscriberDeleteView.as_view(), name='newsletter_subscriber_delete'),

    
    # CMS Content
    path('cms/', cms.CmsDashboardView.as_view(), name='cms_dashboard'),
    path('cms/hero/add/', cms.HeroSlideCreateView.as_view(), name='hero_create'),
    path('cms/hero/<int:pk>/edit/', cms.HeroSlideUpdateView.as_view(), name='hero_edit'),
    path('cms/hero/<int:pk>/delete/', cms.HeroSlideDeleteView.as_view(), name='hero_delete'),
    path('cms/about/', cms.AboutPreviewUpdateView.as_view(), name='about_update'),
    path('cms/about-cms/', cms.AboutCMSUpdateView.as_view(), name='about_cms_update'),
    path('cms/team-member/add/', cms.TeamMemberCreateView.as_view(), name='team_member_create'),
    path('cms/team-member/<int:pk>/edit/', cms.TeamMemberUpdateView.as_view(), name='team_member_edit'),
    path('cms/team-member/<int:pk>/delete/', cms.TeamMemberDeleteView.as_view(), name='team_member_delete'),
    path('cms/sustainability-cms/', cms.SustainabilityCMSUpdateView.as_view(), name='sustainability_cms_update'),
    path('cms/sustainability-pillar/add/', cms.SustainabilityPillarCreateView.as_view(), name='sustainability_pillar_create'),
    path('cms/sustainability-pillar/<int:pk>/edit/', cms.SustainabilityPillarUpdateView.as_view(), name='sustainability_pillar_edit'),
    path('cms/sustainability-pillar/<int:pk>/delete/', cms.SustainabilityPillarDeleteView.as_view(), name='sustainability_pillar_delete'),
    
    path('cms/testimonial/add/', cms.TestimonialCreateView.as_view(), name='testimonial_create'),
    path('cms/testimonial/<int:pk>/edit/', cms.TestimonialUpdateView.as_view(), name='testimonial_edit'),
    path('cms/testimonial/<int:pk>/delete/', cms.TestimonialDeleteView.as_view(), name='testimonial_delete'),
    
    path('cms/gallery/category/add/', cms.GalleryCategoryCreateView.as_view(), name='gallery_category_create'),
    path('cms/gallery/category/<int:pk>/edit/', cms.GalleryCategoryUpdateView.as_view(), name='gallery_category_edit'),
    path('cms/gallery/category/<int:pk>/delete/', cms.GalleryCategoryDeleteView.as_view(), name='gallery_category_delete'),
    
    path('cms/gallery/add/', cms.GalleryItemCreateView.as_view(), name='gallery_create'),
    path('cms/gallery/bulk/', cms.GalleryItemBulkUploadView.as_view(), name='gallery_bulk_upload'),
    path('cms/gallery/<int:pk>/delete/', cms.GalleryItemDeleteView.as_view(), name='gallery_delete'),
    
    path('cms/seo/add/', cms.SeoCreateView.as_view(), name='seo_create'),
    path('cms/seo/<int:pk>/edit/', cms.SeoUpdateView.as_view(), name='seo_edit'),
    path('cms/seo/<int:pk>/delete/', cms.SeoDeleteView.as_view(), name='seo_delete'),
    
    # Users
    path('users/', users.UserListView.as_view(), name='user_list'),
    path('users/add/', users.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', users.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', users.UserDeleteView.as_view(), name='user_delete'),
    
    # Settings Manager
    path('settings/', settings.SettingsDashboardView.as_view(), name='settings_dashboard'),
    path('settings/currency/add/', settings.CurrencyCreateView.as_view(), name='currency_create'),
    path('settings/currency/<int:pk>/edit/', settings.CurrencyUpdateView.as_view(), name='currency_edit'),
    path('settings/currency/<int:pk>/delete/', settings.CurrencyDeleteView.as_view(), name='currency_delete'),
    path('settings/menu/add/', settings.NavigationMenuCreateView.as_view(), name='menu_create'),
    path('settings/menu/<int:pk>/edit/', settings.NavigationMenuUpdateView.as_view(), name='menu_edit'),
    path('settings/menu/<int:pk>/delete/', settings.NavigationMenuDeleteView.as_view(), name='menu_delete'),
    
    path('settings/processor/add/', settings.PaymentProcessorCreateView.as_view(), name='processor_create'),
    path('settings/processor/<int:pk>/edit/', settings.PaymentProcessorUpdateView.as_view(), name='processor_edit'),
    path('settings/processor/<int:pk>/delete/', settings.PaymentProcessorDeleteView.as_view(), name='processor_delete'),
]
