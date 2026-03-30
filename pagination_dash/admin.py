from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PaginationReport, GNPInformation, BookDetails, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline editor for UserProfile within User admin"""
    model = UserProfile
    can_delete = False
    verbose_name = "Plant Access Profile"
    verbose_name_plural = "Plant Access Profile"
    fields = ['allowed_plants', 'is_plant_admin']

    # This prevents Django from trying to create duplicate profiles
    max_num = 1
    min_num = 1

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Customize the allowed_plants field to show as a textarea"""
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'allowed_plants':
            formfield.help_text = (
                'Enter plant IDs as a JSON array, e.g., ["ODBCAIR30", "MAIN34"]. '
                'Leave empty [] if user should have no plant access. '
                'Staff, superusers, and plant admins have access to all plants.'
            )
        return formfield


class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin with UserProfile inline"""
    inlines = (UserProfileInline,)

    def save_model(self, request, obj, form, change):
        """Save the user"""
        super().save_model(request, obj, form, change)
        # Note: UserProfile is created automatically via the inline form
        # No need to manually create it here

    list_display = BaseUserAdmin.list_display + ('get_plant_count', 'get_is_plant_admin')

    def get_plant_count(self, obj):
        """Display number of plants user can access"""
        if hasattr(obj, 'profile'):
            if obj.is_staff or obj.is_superuser or obj.profile.is_plant_admin:
                return "All (Admin)"
            return len(obj.profile.allowed_plants)
        return 0
    get_plant_count.short_description = 'Plant Access'

    def get_is_plant_admin(self, obj):
        """Display if user is plant admin"""
        if hasattr(obj, 'profile'):
            return obj.profile.is_plant_admin
        return False
    get_is_plant_admin.short_description = 'Plant Admin'
    get_is_plant_admin.boolean = True


# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Standalone admin for UserProfile"""
    list_display = ['user', 'is_plant_admin', 'get_allowed_plants_display', 'updated_at']
    list_filter = ['is_plant_admin', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Plant Access', {
            'fields': ('allowed_plants', 'is_plant_admin'),
            'description': 'Configure which plants this user can access. Plant admins, staff, and superusers can access all plants.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_allowed_plants_display(self, obj):
        """Display allowed plants in a readable format"""
        if obj.is_plant_admin or obj.user.is_staff or obj.user.is_superuser:
            return "All Plants (Admin Access)"
        if not obj.allowed_plants:
            return "No Access"
        return ", ".join(obj.allowed_plants)
    get_allowed_plants_display.short_description = 'Allowed Plants'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Customize the allowed_plants field"""
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'allowed_plants':
            formfield.help_text = (
                'Enter plant IDs as a JSON array, e.g., ["ODBCAIR30", "MAIN34", "MAIN35"]. '
                'Available plant IDs: ODBCAIR30, ACTIVE42, ODBCAIR32, MAIN34, MAIN38, '
                'MAIN35, MAIN40, ODBCAIR28, ACTIVE44, MAIN36, MAIN41, ODBCAIR33, ACTIVE43, MAIN37'
            )
        return formfield


class GNPInformationInline(admin.StackedInline):
    """Inline editor for GNP Information within PaginationReport"""
    model = GNPInformation
    can_delete = False
    verbose_name = "GNP Information"
    verbose_name_plural = "GNP Information"
    fields = [('et', 'mt', 'mirror', 'nbt', 'tims'), 'remarks']


class BookDetailsInline(admin.TabularInline):
    """Inline tabular editor for Book Details within PaginationReport"""
    model = BookDetails
    extra = 3
    ordering = ['order']
    fields = ['order', 'book_name', 'snp_pages', 'gnp_pages_type', 'gnp_pages_count', 'total_pages', 'number_of_gnp_jackets']
    readonly_fields = ['gnp_pages_count', 'total_pages']

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }


@admin.register(PaginationReport)
class PaginationReportAdmin(admin.ModelAdmin):
    """Admin interface for PaginationReport with inline editors"""

    list_display = [
        'plant_name',
        'issue_date',
        'get_total_books',
        'get_total_snp',
        'get_total_gnp',
        'get_total_pages_display',
        'created_at',
        'created_by'
    ]

    list_filter = [
        'plant_id',
        'plant_name',
        'issue_date',
        'created_at'
    ]

    search_fields = [
        'plant_name',
        'plant_id',
        'issue_date',
        'remarks_toi',
        'remarks_others'
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'get_total_books',
        'get_total_snp',
        'get_total_gnp',
        'get_total_pages_display',
        'get_total_jackets'
    ]

    fieldsets = (
        ('Plant Information', {
            'fields': ('plant_id', 'plant_name', 'issue_date')
        }),
        ('Remarks', {
            'fields': ('remarks_toi', 'remarks_others', 'first_time_execution_info', 'auto_collated_groups'),
            'classes': ('collapse',)
        }),
        ('Totals (Calculated)', {
            'fields': (
                ('get_total_books', 'get_total_snp'),
                ('get_total_gnp', 'get_total_pages_display'),
                'get_total_jackets'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    inlines = [GNPInformationInline, BookDetailsInline]

    date_hierarchy = 'issue_date'
    ordering = ['-issue_date', 'plant_name']
    list_per_page = 20

    def get_total_books(self, obj):
        """Display total number of books"""
        return obj.get_book_count()
    get_total_books.short_description = 'Books'
    get_total_books.admin_order_field = 'books'

    def get_total_snp(self, obj):
        """Display total SNP pages"""
        return obj.get_total_snp_pages()
    get_total_snp.short_description = 'SNP Pages'

    def get_total_gnp(self, obj):
        """Display total GNP pages"""
        return obj.get_total_gnp_pages()
    get_total_gnp.short_description = 'GNP Pages'

    def get_total_pages_display(self, obj):
        """Display total pages"""
        return obj.get_total_pages()
    get_total_pages_display.short_description = 'Total Pages'

    def get_total_jackets(self, obj):
        """Display total GNP jackets"""
        return obj.get_total_gnp_jackets()
    get_total_jackets.short_description = 'Total Jackets'

    def save_model(self, request, obj, form, change):
        """Auto-populate created_by field if not set"""
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BookDetails)
class BookDetailsAdmin(admin.ModelAdmin):
    """Admin interface for standalone Book Details management"""

    list_display = [
        'report',
        'book_name',
        'order',
        'snp_pages',
        'gnp_pages_type',
        'gnp_pages_count',
        'total_pages',
        'number_of_gnp_jackets'
    ]

    list_filter = [
        'book_name',
        'report__plant_id',
        'report__plant_name',
        'gnp_pages_type'
    ]

    search_fields = [
        'report__plant_name',
        'book_name',
        'report__issue_date'
    ]

    readonly_fields = ['gnp_pages_count', 'total_pages']

    fieldsets = (
        ('Report Information', {
            'fields': ('report', 'book_name', 'order')
        }),
        ('Page Details', {
            'fields': (
                'snp_pages',
                'gnp_pages_type',
                'gnp_pages_count',
                'total_pages',
                'number_of_gnp_jackets'
            )
        }),
    )

    ordering = ['report__issue_date', 'report__plant_name', 'order']
    list_per_page = 50

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('report')


@admin.register(GNPInformation)
class GNPInformationAdmin(admin.ModelAdmin):
    """Admin interface for GNP Information"""

    list_display = [
        'report',
        'et',
        'mt',
        'mirror',
        'nbt',
        'tims',
        'get_active_count'
    ]

    list_filter = [
        'et',
        'mt',
        'mirror',
        'nbt',
        'tims',
        'report__plant_name'
    ]

    search_fields = [
        'report__plant_name',
        'report__issue_date',
        'remarks'
    ]

    fieldsets = (
        ('Report', {
            'fields': ('report',)
        }),
        ('Publications', {
            'fields': (('et', 'mt', 'mirror'), ('nbt', 'tims'))
        }),
        ('Remarks', {
            'fields': ('remarks',)
        }),
    )

    def get_active_count(self, obj):
        """Display count of active publications"""
        return len(obj.get_active_publications())
    get_active_count.short_description = 'Active Publications'

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('report')
