from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class UserProfile(models.Model):
    """
    User profile for location-based access control.
    Stores which plants a user can access and admin status.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    allowed_plants = models.JSONField(
        default=list,
        help_text="List of plant IDs this user can access (e.g., ['ODBCAIR30', 'MAIN34'])"
    )
    is_plant_admin = models.BooleanField(
        default=False,
        help_text="Can access all plants and the plant selection page"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def has_plant_access(self, plant_id):
        """Check if user has access to a specific plant"""
        if self.is_plant_admin or self.user.is_staff or self.user.is_superuser:
            return True
        return plant_id in self.allowed_plants

    def get_accessible_plants(self):
        """Get list of plant IDs user can access"""
        if self.is_plant_admin or self.user.is_staff or self.user.is_superuser:
            from upload_from_pi.plant_ids import plant_details
            return [plant['id'] for plant in plant_details]
        return self.allowed_plants

    def __str__(self):
        return f"{self.user.username} - Profile"


class PaginationReport(models.Model):
    """
    Main record for each daily pagination submission per plant.
    Stores plant information, issue date, and remarks.
    """
    plant_id = models.CharField(max_length=20, help_text="Plant ID from plant_details (e.g., ODBCAIR30)")
    plant_name = models.CharField(max_length=100, help_text="Display name (e.g., Airoli)")
    issue_date = models.DateField(help_text="Issue date for the report")
    remarks_toi = models.TextField(blank=True, null=True, help_text="Remarks for TOI publications")
    remarks_others = models.TextField(blank=True, null=True, help_text="Remarks for other publications")
    first_time_execution_info = models.TextField(blank=True, null=True, help_text="First-time execution details")
    auto_collated_groups = models.JSONField(
        default=list,
        blank=True,
        help_text="List of auto-collated book groups (each group is a list of book names)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagination_reports')

    class Meta:
        db_table = 'pagination_report'
        unique_together = [['plant_id', 'issue_date']]
        indexes = [
            models.Index(fields=['plant_id', 'issue_date']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['plant_id']),
        ]
        ordering = ['-issue_date', 'plant_name']
        verbose_name = 'Pagination Report'
        verbose_name_plural = 'Pagination Reports'

    def get_total_snp_pages(self):
        """Sum of all SNP pages across books"""
        return self.books.aggregate(total=models.Sum('snp_pages'))['total'] or 0

    def get_total_gnp_pages(self):
        """Sum of all GNP page counts across books"""
        return self.books.aggregate(total=models.Sum('gnp_pages_count'))['total'] or 0

    def get_total_pages(self):
        """Sum of all total pages across books"""
        return self.books.aggregate(total=models.Sum('total_pages'))['total'] or 0

    def get_total_gnp_jackets(self):
        """Sum of all GNP jackets across books"""
        return self.books.aggregate(total=models.Sum('number_of_gnp_jackets'))['total'] or 0

    def get_book_count(self):
        """Count of books in this report"""
        return self.books.count()

    def get_competitor_count(self):
        """Count of competitor entries in this report"""
        return self.competitors.count()

    def __str__(self):
        return f"{self.plant_name} - {self.issue_date}"


class GNPInformation(models.Model):
    """
    Store GNP-related boolean flags and remarks for each report.
    One-to-One relationship with PaginationReport.
    """
    report = models.OneToOneField(
        PaginationReport,
        on_delete=models.CASCADE,
        related_name='gnp_info',
        primary_key=True
    )
    et = models.BooleanField(default=False, verbose_name="Economic Times")
    et_b1 = models.BooleanField(default=False, verbose_name="ET B-1", help_text="ET Book 1 had GNP")
    et_b2 = models.BooleanField(default=False, verbose_name="ET B-2", help_text="ET Book 2 had GNP")
    mt = models.BooleanField(default=False, verbose_name="Maharashtra Times")
    mirror = models.BooleanField(default=False, verbose_name="Mirror")
    nbt = models.BooleanField(default=False, verbose_name="Navbharat Times")
    tims = models.BooleanField(default=False, verbose_name="TIMS")
    et_had_2_books = models.BooleanField(
        default=False,
        verbose_name="ET had 2 Books",
        help_text="Indicates if Economic Times publication had 2 books"
    )
    remarks = models.TextField(blank=True, null=True, help_text="GNP-specific remarks")

    class Meta:
        db_table = 'gnp_information'
        verbose_name = 'GNP Information'
        verbose_name_plural = 'GNP Information'

    def get_active_publications(self):
        """Return list of publication names where flag is True"""
        publications = []
        if self.et:
            publications.append('Economic Times')
        if self.et_b1:
            publications.append('ET B-1')
        if self.et_b2:
            publications.append('ET B-2')
        if self.mt:
            publications.append('Maharashtra Times')
        if self.mirror:
            publications.append('Mirror')
        if self.nbt:
            publications.append('Navbharat Times')
        if self.tims:
            publications.append('TIMS')
        return publications

    def __str__(self):
        return f"GNP Info - {self.report}"


class BookDetails(models.Model):
    """
    Store individual book information for each pagination report.
    Many-to-One relationship with PaginationReport.
    """

    # Book name choices
    BOOK_NAME_CHOICES = [
        ('TOI B-1', 'TOI B-1'),
        ('TOI B-2', 'TOI B-2'),
        ('TIMS B-1', 'TIMS B-1'),
        ('TIMS B-2', 'TIMS B-2'),
        ('TOI Supp-1', 'TOI Supp-1'),
        ('TOI Supp-2', 'TOI Supp-2'),
        ('TOI Supp-3', 'TOI Supp-3'),
    ]

    # GNP type choices with corresponding page counts
    GNP_TYPE_CHOICES = [
        ('2 Pg Jkt', '2 Pg Jkt'),
        ('4 Pg Jkt - 2 diff clients', '4 Pg Jkt - 2 diff clients'),
        ('4 Pg Vantage', '4 Pg Vantage'),
        ('4 Pg Power Jkt', '4 Pg Power Jkt'),
        ('8 Pg Super-pano', '8 Pg Super-pano'),
        ('6 Pg GNP', '6 Pg GNP'),
        ('8 Pg GNP', '8 Pg GNP'),
    ]

    # GNP type to page count mapping
    GNP_TYPE_PAGE_MAPPING = {
        '2 Pg Jkt': 2,
        '4 Pg Jkt - 2 diff clients': 4,
        '4 Pg Vantage': 4,
        '4 Pg Power Jkt': 4,
        '8 Pg Super-pano': 8,
        '6 Pg GNP': 6,
        '8 Pg GNP': 8,
    }

    report = models.ForeignKey(
        PaginationReport,
        on_delete=models.CASCADE,
        related_name='books'
    )
    book_name = models.CharField(max_length=50, choices=BOOK_NAME_CHOICES)
    snp_pages = models.PositiveIntegerField(default=0, help_text="Standard News Pages")
    gnp_pages_type = models.CharField(
        max_length=50,
        choices=GNP_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="GNP Pages Type"
    )
    gnp_pages_count = models.PositiveIntegerField(
        default=0,
        help_text="Auto-populated based on GNP type"
    )
    total_pages = models.PositiveIntegerField(
        default=0,
        help_text="SNP Pages + GNP Pages Count"
    )
    number_of_gnp_jackets = models.PositiveIntegerField(default=0, verbose_name="Number of GNP Jackets")
    balloon_printed = models.BooleanField(
        default=False,
        verbose_name="Balloon Printed",
        help_text="Indicates if balloon was printed (only for TOI B-2 or TIMS B-2)"
    )
    has_masthead = models.BooleanField(
        default=False,
        verbose_name="Has Masthead",
        help_text="Indicates if masthead is present (only for TOI B-2 or TIMS B-2)"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order")

    class Meta:
        db_table = 'book_details'
        indexes = [
            models.Index(fields=['report', 'book_name']),
            models.Index(fields=['order']),
        ]
        ordering = ['order', 'id']
        verbose_name = 'Book Details'
        verbose_name_plural = 'Book Details'

    def clean(self):
        """
        Validate book details:
        - No duplicate book names within same report (database check as safety net)
        - If GNP type is selected, jacket count should be > 0 (warning, not error)

        Note: Formset-level validation also checks for duplicates within the same submission.
        This model-level validation acts as a safety net for database integrity.
        """
        super().clean()

        # Check for duplicate book names in the database (safety net)
        # Formset validation handles duplicates within the same submission
        if self.report_id and self.book_name:
            duplicate_books = BookDetails.objects.filter(
                report=self.report,
                book_name=self.book_name
            )

            # If this is an update (instance has pk), exclude current instance
            if self.pk:
                duplicate_books = duplicate_books.exclude(pk=self.pk)

            if duplicate_books.exists():
                raise ValidationError({
                    'book_name': f'A book with name "{self.book_name}" already exists in this report.'
                })

    def get_gnp_page_count_from_type(self):
        """Map GNP type to numeric page count"""
        if not self.gnp_pages_type:
            return 0
        return self.GNP_TYPE_PAGE_MAPPING.get(self.gnp_pages_type, 0)

    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate fields:
        - gnp_pages_count from gnp_pages_type
        - total_pages from snp_pages + gnp_pages_count
        """
        # Auto-populate gnp_pages_count from type
        if self.gnp_pages_type:
            self.gnp_pages_count = self.get_gnp_page_count_from_type()
        else:
            self.gnp_pages_count = 0

        # Auto-calculate total_pages
        self.total_pages = self.snp_pages + self.gnp_pages_count

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book_name} - {self.report}"


class CompetitorData(models.Model):
    """
    Store competitor pagination data for each report.
    Many-to-One relationship with PaginationReport.
    Competitor names vary by plant location (defined in comp_info.json).
    Book-level details stored in CompetitorBookDetails model.
    """

    # Innovation choices
    INNOVATION_CHOICES = [
        ('Center Panorama', 'Center Panorama'),
        ('Bookmark', 'Bookmark'),
        ('Seamless Panorama', 'Seamless Panorama'),
        ('Front Vantage', 'Front Vantage'),
        ('Reverse Flap', 'Reverse Flap'),
        ('Fragrance', 'Fragrance'),
        ('French-Window', 'French-Window'),
        ('Power Jacket', 'Power Jacket'),
        ('Others', 'Others')
    ]

    report = models.ForeignKey(
        PaginationReport,
        on_delete=models.CASCADE,
        related_name='competitors'
    )
    competitor_name = models.CharField(
        max_length=100,
        help_text="Competitor newspaper name"
    )
    innovation = models.JSONField(
        blank=True,
        null=True,
        default=list,
        verbose_name="Innovation",
        help_text="Multiple innovation types (stored as JSON array)"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Additional comments about competitor"
    )

    class Meta:
        db_table = 'competitor_data'
        indexes = [
            models.Index(fields=['report', 'competitor_name']),
        ]
        ordering = ['id']
        verbose_name = 'Competitor Data'
        verbose_name_plural = 'Competitor Data'

    def clean(self):
        """
        Validate competitor data:
        - No duplicate competitor names within same report (database check as safety net)

        Note: Formset-level validation also checks for duplicates within the same submission.
        This model-level validation acts as a safety net for database integrity.
        """
        super().clean()

        # Check for duplicate competitor names in the database (safety net)
        # Formset validation handles duplicates within the same submission
        if self.report_id and self.competitor_name:
            duplicate_competitors = CompetitorData.objects.filter(
                report=self.report,
                competitor_name=self.competitor_name
            )

            # If this is an update (instance has pk), exclude current instance
            if self.pk:
                duplicate_competitors = duplicate_competitors.exclude(pk=self.pk)

            if duplicate_competitors.exists():
                raise ValidationError({
                    'competitor_name': f'Competitor "{self.competitor_name}" already exists in this report.'
                })

    def get_total_pages(self):
        """Calculate total pages across all book details (Main + Supplement)"""
        return self.book_details.aggregate(total=models.Sum('total_pages'))['total'] or 0

    def get_main_book(self):
        """Get Main book details"""
        return self.book_details.filter(book_type='Main').first()

    def get_supplement_book(self):
        """Get Supplement book details"""
        return self.book_details.filter(book_type='Supplement').first()

    @property
    def snp_pages(self):
        """Calculate total SNP pages across all book details"""
        return self.book_details.aggregate(total=models.Sum('snp_pages'))['total'] or 0

    @property
    def gnp_pages(self):
        """Calculate total GNP pages across all book details"""
        return self.book_details.aggregate(total=models.Sum('gnp_pages_count'))['total'] or 0

    @property
    def total_pages(self):
        """Calculate total pages across all book details"""
        return self.get_total_pages()

    @property
    def gnp_jkts_main(self):
        """Get GNP jacket count from Main book"""
        main_book = self.get_main_book()
        return main_book.number_of_gnp_jacket if main_book else 0

    @property
    def gnp_jkts_supplement(self):
        """Get GNP jacket count from Supplement book"""
        supplement_book = self.get_supplement_book()
        return supplement_book.number_of_gnp_jacket if supplement_book else 0

    @property
    def total_gnp_jkts(self):
        """Calculate total GNP jackets across all book details"""
        return self.book_details.aggregate(total=models.Sum('number_of_gnp_jacket'))['total'] or 0

    @property
    def books_main(self):
        """Get number of books from Main book"""
        main_book = self.get_main_book()
        return main_book.number_of_books if main_book else 0

    @property
    def books_supplement(self):
        """Get number of books from Supplement book"""
        supplement_book = self.get_supplement_book()
        return supplement_book.number_of_books if supplement_book else 0

    @property
    def total_books(self):
        """Calculate total number of books across all book details"""
        return self.book_details.aggregate(total=models.Sum('number_of_books'))['total'] or 0

    def __str__(self):
        return f"{self.competitor_name} - {self.report}"


class CompetitorBookDetails(models.Model):
    """
    Store book-level pagination data for each competitor.
    Each competitor has 2 book types: Main and Supplement.
    Many-to-One relationship with CompetitorData.
    """

    # Book type choices
    BOOK_TYPE_CHOICES = [
        ('Main', 'Main'),
        ('Supplement', 'Supplement'),
    ]

    competitor = models.ForeignKey(
        CompetitorData,
        on_delete=models.CASCADE,
        related_name='book_details'
    )
    book_type = models.CharField(
        max_length=20,
        choices=BOOK_TYPE_CHOICES,
        help_text="Book type: Main or Supplement"
    )
    snp_pages = models.PositiveIntegerField(
        default=0,
        verbose_name="SNP Pages",
        help_text="Standard News Pages"
    )
    gnp_pages_type = models.CharField(
        max_length=50,
        choices=BookDetails.GNP_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="GNP Pages Type"
    )
    gnp_pages_count = models.PositiveIntegerField(
        default=0,
        help_text="Auto-populated based on GNP type"
    )
    total_pages = models.PositiveIntegerField(
        default=0,
        help_text="SNP Pages + GNP Pages Count"
    )
    number_of_gnp_jacket = models.PositiveIntegerField(
        default=0,
        verbose_name="Number of GNP Jacket",
        help_text="Number of GNP jackets for competitor"
    )
    number_of_books = models.PositiveIntegerField(
        default=0,
        verbose_name="Number of Books",
        help_text="Total number of books for competitor"
    )

    class Meta:
        db_table = 'competitor_book_details'
        indexes = [
            models.Index(fields=['competitor', 'book_type']),
        ]
        ordering = ['book_type']
        verbose_name = 'Competitor Book Details'
        verbose_name_plural = 'Competitor Book Details'
        unique_together = [['competitor', 'book_type']]

    def clean(self):
        """
        Validate book details:
        - No duplicate book types within same competitor
        """
        super().clean()

        # Check for duplicate book types for the same competitor
        if self.competitor_id and self.book_type:
            duplicate_books = CompetitorBookDetails.objects.filter(
                competitor=self.competitor,
                book_type=self.book_type
            )

            # If this is an update (instance has pk), exclude current instance
            if self.pk:
                duplicate_books = duplicate_books.exclude(pk=self.pk)

            if duplicate_books.exists():
                raise ValidationError({
                    'book_type': f'A "{self.book_type}" book already exists for this competitor.'
                })

    def get_gnp_page_count_from_type(self):
        """Map GNP type to numeric page count using BookDetails mapping"""
        if not self.gnp_pages_type:
            return 0
        return BookDetails.GNP_TYPE_PAGE_MAPPING.get(self.gnp_pages_type, 0)

    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate fields:
        - gnp_pages_count from gnp_pages_type
        - total_pages from snp_pages + gnp_pages_count
        """
        # Auto-populate gnp_pages_count from type
        if self.gnp_pages_type:
            self.gnp_pages_count = self.get_gnp_page_count_from_type()
        else:
            self.gnp_pages_count = 0

        # Auto-calculate total_pages
        self.total_pages = self.snp_pages + self.gnp_pages_count

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.competitor.competitor_name} - {self.book_type} - {self.competitor.report}"
