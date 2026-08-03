from django.db import models
from core.utils import UploadTo, ValidateFileSize

class ZiplineCMS(models.Model):
    hero_subtitle = models.CharField(max_length=150, default="Nagarkot Adventure Destination")
    hero_title = models.CharField(max_length=150, default="Nagarkot Zipline: The Superman Zip Line")
    hero_description = models.TextField(default="Soar through the skies of Nagarkot above lush pine forests with panoramic views of the Himalayan range and Mount Everest.")
    hero_image = models.ImageField(upload_to=UploadTo('zipline/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])

    # Video Preview (YouTube/Vimeo or uploaded MP4)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube, Vimeo, or external MP4 URL for Zipline video preview")
    video_file = models.FileField(upload_to=UploadTo('zipline/videos'), blank=True, null=True, help_text="Upload MP4 video file to play on the Zipline page")

    spec_length = models.CharField(max_length=50, default="1,200 Meters")
    spec_length_label = models.CharField(max_length=50, default="Flight Length")

    spec_speed = models.CharField(max_length=50, default="95 KM/H")
    spec_speed_label = models.CharField(max_length=50, default="Top Speed")

    spec_elevation = models.CharField(max_length=50, default="2,175m Altitude")
    spec_elevation_label = models.CharField(max_length=50, default="Altitude Elevation")

    spec_safety = models.CharField(max_length=50, default="100% International Certified")
    spec_safety_label = models.CharField(max_length=50, default="Safety Standard")

    # Homepage teaser section (the right column on the homepage)
    homepage_badge_text = models.CharField(
        max_length=120,
        default="2nd Destination • Nagarkot Zipline",
        help_text="Badge label shown above the heading on the homepage zipline section",
    )
    homepage_heading = models.CharField(
        max_length=200,
        default="Nepal's Longest Zipline Flight",
        help_text="Main heading for the zipline section on the homepage",
    )
    homepage_description = models.TextField(
        default="Soar above lush pine forests facing snow-capped Himalayan peaks. Select a zipline package and book instantly!",
        help_text="Short description shown under the heading on the homepage zipline section",
    )

    booking_url = models.URLField(default="https://www.facebook.com/ziplinenagarkot", help_text="External URL for booking zipline (e.g. Facebook page or booking engine)")
    booking_button_text = models.CharField(max_length=100, default="Book Zipline Flight / Facebook Page")

    overview_subtitle = models.CharField(max_length=150, default="High-Altitude Thrill")
    overview_title = models.CharField(max_length=200, default="Nepal's Longest Superman Flight Zipline")
    overview_content = models.TextField(default="Located just 32 kilometers from Kathmandu at Changunarayan-7, Nagarkot, Nagarkot Zipline offers one of South Asia's most thrilling high-altitude zipline experiences. Choose between Superman Flight position, Tandem dual flight, or Classic harness zip as you glide above pine forests facing snow-capped peaks.")
    overview_image = models.ImageField(upload_to=UploadTo('zipline/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])
    image_caption_title = models.CharField(max_length=100, default="Superman Flying Harness", blank=True, null=True)
    image_caption_subtitle = models.CharField(max_length=150, default="Head-first aerial view of Everest range", blank=True, null=True)

    # Legal Waiver & Release Form Document
    waiver_title = models.CharField(max_length=200, default="WAIVER & RELEASE OF LIABILITY FORM")
    waiver_subtitle = models.CharField(max_length=200, default="PARTICIPANT USER AGREEMENT")
    waiver_text = models.TextField(
        default="In consideration of NAGARKOT ZIPLINE PVT. LTD furnishing services and/or equipment to enable me to participate in activities associated with or enter upon the lands of NAGARKOT ZIPLINE PVT. LTD., their agents, owners, associates and all other persons or entities acting in any capacity on their behalf (hereinafter collectively referred to as \"Zip Line Tour\"), I hereby voluntarily agree to release, discharge, hold harmless and covenant not to sue Zip Line Tour on behalf of myself, my children, my parents, my heirs, assigns, personal representatives and/or estate for any and all claims of liability arising out of negligence, recklessness, strict liability, breach of contract, intentional acts or any other act or omission which causes illness, injury, death or damage of any nature in any way connected with my participation in this activity.\n\nI fully understand and acknowledge that:\nA. Outdoor recreational activities such as zip lines, canopy tours, challenge courses, mountain hiking and exploring have inherent risks, dangers and hazards, and such risks may exist in my use of NAGARKOT ZIPLINE PVT. LTD. property and equipment.\nB. My participation in such activities and/or use of such equipment may result in injury or illness including, but not limited to, body injury, strains, fractures, partial or total paralysis, death, exposure to insects and snake bites, extreme temperatures, slips and falls, encounters with animals, collisions, and remote area medical limitations.\nC. These risks and dangers may be caused by negligence of the owners, employees, officers or agents of NAGARKOT ZIPLINE PVT. LTD., negligence of participants, accidents, breaches of contract, forces of nature, or other causes, whether foreseeable or unforeseeable.\nD. By participating in these activities, I assume all risks and responsibility for any loss or damage whether caused in whole or in part by negligence or other conduct of NAGARKOT ZIPLINE PVT. LTD. I also grant permission to NAGARKOT ZIPLINE PVT. LTD. to use photographs or recordings for promotional purposes without compensation.\n\nI have read the above and fully understand that by signing this document I am waiving legal rights and confirm that I choose to sign it freely and voluntarily in full knowledge of the risks.",
        help_text="Full legal terms text displayed inside the Zipline Booking Waiver Modal"
    )

    # Flight Slot Options
    available_time_slots = models.TextField(
        default="Morning (09:00 AM - 12:00 PM)\nAfternoon (12:00 PM - 03:00 PM)\nSunset Flight (03:00 PM - 06:00 PM)",
        help_text="Time slots for zipline booking (one slot option per line)"
    )

    @property
    def time_slots_list(self):
        if not self.available_time_slots:
            return ["Morning (09:00 AM - 12:00 PM)", "Afternoon (12:00 PM - 03:00 PM)", "Sunset Flight (03:00 PM - 06:00 PM)"]
        slots = [s.strip() for s in self.available_time_slots.splitlines() if s.strip()]
        return slots if slots else ["Morning (09:00 AM - 12:00 PM)", "Afternoon (12:00 PM - 03:00 PM)", "Sunset Flight (03:00 PM - 06:00 PM)"]

    class Meta:
        verbose_name = "Zipline Page Content CMS"
        verbose_name_plural = "Zipline Page Content CMS"

    def __str__(self):
        return "Zipline Page Content CMS Settings"

    def save(self, *args, **kwargs):
        if not self.pk and ZiplineCMS.objects.exists():
            # pyrefly: ignore [missing-attribute]
            self.pk = ZiplineCMS.objects.first().pk
        super().save(*args, **kwargs)
