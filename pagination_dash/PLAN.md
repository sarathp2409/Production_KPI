# Pagination Data Collection CRUD Application - Implementation Plan

## Executive Summary

This document outlines the comprehensive implementation plan for a CRUD (Create, Read, Update, Delete) application to collect and maintain pagination-related data from 14 printing plants. The application will be built within the `pagination_dash` Django app and will provide plant-specific URLs to ensure data integrity and prevent accidental cross-plant data entry.

## 1. Business Requirements

### 1.1 Overview
- Collect pagination data from 14 different printing plants
- Provide unique URLs for each plant location
- Support multiple book entries per submission
- Track GNP (Good News Pages) information
- Calculate totals automatically
- Maintain historical records with full CRUD capabilities

### 1.2 Plant Details
Based on `plant_ids.py`, the following 14 plants will be supported:
1. Airoli (ODBCAIR30)
2. Baroda (ACTIVE42)
3. Pune/Bhosari (ODBCAIR32)
4. Bangalore/Bommasandra (MAIN34)
5. Nagpur/Butibori (MAIN38)
6. Chennai/Chemmencherry (MAIN35)
7. Lucknow/Chinhat (MAIN40)
8. Kandivali (ODBCAIR28)
9. Manesar (ACTIVE44)
10. Hyderabad/Nacharam (MAIN36)
11. Sahibabad (MAIN41)
12. Kolkata/Saltlake (ODBCAIR33)
13. Trivandrum (ACTIVE43)
14. Ahmedabad/Vejalpur (MAIN37)

## 2. Database Design

### 2.1 Entity Relationship Design

```
PaginationReport (1) ←→ (1) GNPInformation
PaginationReport (1) ←→ (M) BookDetails
```

### 2.2 Model Specifications

#### 2.2.1 PaginationReport Model
**Purpose**: Main record for each daily pagination submission per plant

**Fields**:
- `id`: BigAutoField (Primary Key)
- `plant_id`: CharField(max_length=20) - From plant_details (e.g., "ODBCAIR30")
- `plant_name`: CharField(max_length=100) - Display name (e.g., "Airoli")
- `issue_date`: DateField - Issue date for the report
- `remarks_toi`: TextField(blank=True, null=True) - Remarks for TOI publications
- `remarks_others`: TextField(blank=True, null=True) - Remarks for other publications
- `first_time_execution_info`: TextField(blank=True, null=True) - First-time execution details
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)
- `created_by`: ForeignKey(User, null=True, blank=True)

**Constraints**:
- Unique together: (plant_id, issue_date)
- Index on: plant_id, issue_date

**Methods**:
- `get_total_snp_pages()`: Sum of all SNP pages across books
- `get_total_gnp_pages()`: Sum of all GNP page counts across books
- `get_total_pages()`: Sum of all total pages across books
- `get_total_gnp_jackets()`: Sum of all GNP jackets across books
- `__str__()`: Return f"{plant_name} - {issue_date}"

#### 2.2.2 GNPInformation Model
**Purpose**: Store GNP-related boolean flags and remarks for each report

**Fields**:
- `id`: BigAutoField (Primary Key)
- `report`: OneToOneField(PaginationReport, on_delete=CASCADE, related_name='gnp_info')
- `et`: BooleanField(default=False) - Economic Times
- `mt`: BooleanField(default=False) - Maharashtra Times
- `mirror`: BooleanField(default=False) - Mirror
- `nbt`: BooleanField(default=False) - Navbharat Times
- `remarks`: TextField(blank=True, null=True)

**Methods**:
- `get_active_publications()`: Return list of publication names where flag is True
- `__str__()`: Return f"GNP Info - {report}"

#### 2.2.3 BookDetails Model
**Purpose**: Store individual book information for each pagination report

**Fields**:
- `id`: BigAutoField (Primary Key)
- `report`: ForeignKey(PaginationReport, on_delete=CASCADE, related_name='books')
- `book_name`: CharField(max_length=50, choices=BOOK_NAME_CHOICES)
- `snp_pages`: PositiveIntegerField(default=0) - Standard News Pages
- `gnp_pages_type`: CharField(max_length=50, choices=GNP_TYPE_CHOICES, blank=True, null=True)
- `gnp_pages_count`: PositiveIntegerField(default=0) - Auto-populated based on type
- `total_pages`: PositiveIntegerField(default=0) - SNP + GNP count
- `number_of_gnp_jackets`: PositiveIntegerField(default=0)
- `order`: PositiveIntegerField(default=0) - For maintaining display order

**Choices**:

BOOK_NAME_CHOICES:
- TOI B-1 (Default)
- TOI B-2 (Default)
- BT B-1 (Default)
- BT B-2 (Additional)
- TOI Supp-1 (Additional)
- TOI Supp-2 (Additional)
- TOI Supp-3 (Additional)

GNP_TYPE_CHOICES:
- 2 Pg Jkt → 2 pages
- 4 Pg Jkt - 2 diff clients → 4 pages
- 4 Pg Vantage → 4 pages
- 4 Pg Power Jkt → 4 pages
- 8 Pg Super-pano → 8 pages
- 6 Pg GNP → 6 pages
- 8 Pg GNP → 8 pages

**Constraints**:
- Index on: report, book_name
- Order by: order, id

**Methods**:
- `save()`: Override to auto-calculate gnp_pages_count and total_pages
- `get_gnp_page_count_from_type()`: Map type to numeric value
- `__str__()`: Return f"{book_name} - {report}"

### 2.3 Database Indexes
```python
# PaginationReport
indexes = [
    models.Index(fields=['plant_id', 'issue_date']),
    models.Index(fields=['issue_date']),
    models.Index(fields=['plant_id']),
]

# BookDetails
indexes = [
    models.Index(fields=['report', 'book_name']),
    models.Index(fields=['order']),
]
```

## 3. URL Structure

### 3.1 URL Patterns
```python
# pagination_dash/urls.py
urlpatterns = [
    # Plant-specific URLs
    path('<str:plant_id>/create/', views.PaginationCreateView.as_view(), name='pagination_create'),
    path('<str:plant_id>/list/', views.PaginationListView.as_view(), name='pagination_list'),
    path('<str:plant_id>/view/<int:pk>/', views.PaginationDetailView.as_view(), name='pagination_detail'),
    path('<str:plant_id>/edit/<int:pk>/', views.PaginationUpdateView.as_view(), name='pagination_update'),
    path('<str:plant_id>/delete/<int:pk>/', views.PaginationDeleteView.as_view(), name='pagination_delete'),

    # Optional: Home page showing all plants
    path('', views.PlantSelectionView.as_view(), name='pagination_home'),
]
```

### 3.2 Example URLs
```
/pagination/ODBCAIR30/create/          # Airoli - Create form
/pagination/ODBCAIR30/list/            # Airoli - List all reports
/pagination/ODBCAIR30/view/123/        # Airoli - View report #123
/pagination/ODBCAIR30/edit/123/        # Airoli - Edit report #123
/pagination/ODBCAIR30/delete/123/      # Airoli - Delete report #123
/pagination/MAIN34/create/             # Bangalore - Create form
```

## 4. Forms Design

### 4.1 Main Form (PaginationReportForm)

**Fields**:
- issue_date: DateField (DateInput widget with date picker)
- remarks_toi: TextField (Textarea widget)
- remarks_others: TextField (Textarea widget)
- first_time_execution_info: TextField (Textarea widget)

**GNP Information** (Inline within main form):
- et: BooleanField (CheckboxInput)
- mt: BooleanField (CheckboxInput)
- mirror: BooleanField (CheckboxInput)
- nbt: BooleanField (CheckboxInput)
- gnp_remarks: TextField (Textarea widget)

**Validation**:
- issue_date: Cannot be future date
- Unique constraint check: plant_id + issue_date combination

### 4.2 Book Details Formset

**Type**: Django Inline Formset (formset_factory)

**Default Rows**: 3 (pre-populated with TOI B-1, TOI B-2, BT B-1)

**Fields per row**:
- book_name: ChoiceField (Select dropdown)
- snp_pages: IntegerField (NumberInput)
- gnp_pages_type: ChoiceField (Select dropdown, optional)
- gnp_pages_count: IntegerField (Read-only, auto-calculated)
- total_pages: IntegerField (Read-only, auto-calculated)
- number_of_gnp_jackets: IntegerField (NumberInput)

**Dynamic Behavior**:
- "Add New Book" button to add additional rows
- Book name choices change based on existing selections
- Additional book choices: BT B-2, TOI Supp-1, TOI Supp-2, TOI Supp-3
- Auto-calculation of gnp_pages_count based on gnp_pages_type
- Auto-calculation of total_pages (SNP + GNP count)
- "Remove" button for rows beyond the default 3

**Validation**:
- At least one book must be entered
- SNP pages must be >= 0
- If GNP type is selected, jacket count should be > 0
- No duplicate book names in same report

## 5. Views Implementation

### 5.1 PlantSelectionView (Optional Landing Page)
**Type**: TemplateView

**Purpose**: Display all 14 plants with links to their respective create/list pages

**Template**: pagination_dash/plant_selection.html

**Context Data**:
- plants: List of all plant details from plant_ids.py

### 5.2 PaginationCreateView
**Type**: CreateView

**Purpose**: Create new pagination report for a specific plant

**Key Features**:
- Validate plant_id against plant_details
- Pre-fill plant_id and plant_name
- Handle main form + GNP info + book formset together
- Transaction-based save (all or nothing)
- Success message on creation

**Form Handling**:
```python
def form_valid(self, form):
    # Begin transaction
    with transaction.atomic():
        # Save main report
        report = form.save(commit=False)
        report.plant_id = self.kwargs['plant_id']
        report.plant_name = self.get_plant_name()
        report.created_by = self.request.user
        report.save()

        # Save GNP info
        gnp_form.instance.report = report
        gnp_form.save()

        # Save book details
        book_formset.instance = report
        book_formset.save()

    return redirect('pagination_list', plant_id=plant_id)
```

### 5.3 PaginationListView
**Type**: ListView

**Purpose**: Display all pagination reports for a specific plant

**Features**:
- Filter by plant_id
- Paginate results (20 per page)
- Search by issue_date
- Sort by issue_date (descending)
- Show summary columns: issue_date, total books, total pages, actions

**QuerySet Optimization**:
- prefetch_related('books', 'gnp_info')
- Annotate with aggregate calculations

### 5.4 PaginationDetailView
**Type**: DetailView

**Purpose**: Display complete read-only view of a pagination report

**Features**:
- Validate plant_id matches report.plant_id
- Display all report details
- Show all books with calculations
- Display GNP information
- Show totals row
- Provide Edit/Delete action buttons

### 5.5 PaginationUpdateView
**Type**: UpdateView

**Purpose**: Edit existing pagination report

**Features**:
- Similar to CreateView but pre-populated
- Validate plant_id matches report.plant_id
- Allow modification of all fields except plant_id
- Handle book additions/deletions
- Transaction-based update

### 5.6 PaginationDeleteView
**Type**: DeleteView

**Purpose**: Delete pagination report with confirmation

**Features**:
- Validate plant_id matches report.plant_id
- Show confirmation page with report details
- Cascade delete (will delete related GNP info and books)
- Success message on deletion

## 6. Templates Structure

### 6.1 Base Template
**File**: pagination_dash/templates/pagination_dash/base.html

**Features**:
- Navigation bar with plant name
- Breadcrumb navigation
- Messages display area (success/error)
- Common CSS/JS includes
- Responsive design (Bootstrap 5 or similar)

### 6.2 Plant Selection Template
**File**: pagination_dash/templates/pagination_dash/plant_selection.html

**Layout**:
- Grid of 14 plant cards
- Each card shows plant name and display name
- Links to Create and List views for each plant

### 6.3 Form Template
**File**: pagination_dash/templates/pagination_dash/pagination_form.html

**Sections**:
1. Header: Plant name, Issue date
2. Book Details Table (with formset)
3. Totals Row (calculated dynamically)
4. GNP Information Section (checkboxes)
5. Remarks Section (TOI and Others)
6. First Time Execution Info
7. Submit/Cancel buttons

**JavaScript Features**:
- Date picker for issue_date
- "Add New Book" button functionality
- "Remove Book" button (for non-default rows)
- Auto-calculation on input change:
  - GNP page count from type
  - Total pages per book
  - Column totals
- Form validation before submission
- AJAX save option (optional enhancement)

### 6.4 List Template
**File**: pagination_dash/templates/pagination_dash/pagination_list.html

**Features**:
- Table with columns: Issue Date, Total Books, Total SNP, Total GNP, Total Pages, Actions
- Search box for date filtering
- Pagination controls
- "Create New" button
- Action buttons: View, Edit, Delete per row

### 6.5 Detail Template
**File**: pagination_dash/templates/pagination_dash/pagination_detail.html

**Layout**:
- Report header (plant, issue date, timestamps)
- Books table (all details)
- Totals row
- GNP Information display
- Remarks sections
- First time execution info
- Action buttons: Edit, Delete, Back to List

### 6.6 Delete Confirmation Template
**File**: pagination_dash/templates/pagination_dash/pagination_confirm_delete.html

**Content**:
- Warning message
- Report summary
- Confirm/Cancel buttons
- Form with CSRF token

## 7. JavaScript Implementation

### 7.1 Core JavaScript File
**File**: pagination_dash/static/pagination_dash/js/pagination_form.js

**Functions**:

```javascript
// Initialize date picker
initDatePicker();

// Add new book row
function addBookRow() {
    // Clone template row
    // Update form prefix/IDs
    // Update book name choices
    // Bind event handlers
    // Update management form
}

// Remove book row
function removeBookRow(rowId) {
    // Remove row from DOM
    // Update management form
    // Recalculate totals
}

// Auto-calculate GNP page count from type
function updateGNPPageCount(selectElement) {
    const typeMapping = {
        '2 Pg Jkt': 2,
        '4 Pg Jkt - 2 diff clients': 4,
        '4 Pg Vantage': 4,
        '4 Pg Power Jkt': 4,
        '8 Pg Super-pano': 8,
        '6 Pg GNP': 6,
        '8 Pg GNP': 8
    };
    // Update corresponding count field
    // Trigger total calculation
}

// Calculate total pages for a book
function calculateBookTotal(rowIndex) {
    const snp = parseInt(getFieldValue('snp_pages', rowIndex)) || 0;
    const gnp = parseInt(getFieldValue('gnp_pages_count', rowIndex)) || 0;
    setFieldValue('total_pages', rowIndex, snp + gnp);
    calculateColumnTotals();
}

// Calculate column totals
function calculateColumnTotals() {
    const totals = {
        snp: 0,
        gnp: 0,
        total: 0,
        jackets: 0
    };
    // Loop through all book rows
    // Sum up each column
    // Update totals row display
}

// Form validation
function validateForm() {
    // Check required fields
    // Validate date
    // Check at least one book
    // Return true/false
}

// Event bindings
$(document).ready(function() {
    // Bind input events for auto-calculation
    // Bind add/remove button clicks
    // Bind form submit
    // Initialize existing rows
});
```

## 8. Admin Interface

### 8.1 Admin Configuration
**File**: pagination_dash/admin.py

```python
from django.contrib import admin
from .models import PaginationReport, GNPInformation, BookDetails

class GNPInformationInline(admin.StackedInline):
    model = GNPInformation
    can_delete = False

class BookDetailsInline(admin.TabularInline):
    model = BookDetails
    extra = 3
    ordering = ['order']

@admin.register(PaginationReport)
class PaginationReportAdmin(admin.ModelAdmin):
    list_display = ['plant_name', 'issue_date', 'get_total_books', 'get_total_pages', 'created_at']
    list_filter = ['plant_id', 'issue_date']
    search_fields = ['plant_name', 'plant_id', 'issue_date']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [GNPInformationInline, BookDetailsInline]

    def get_total_books(self, obj):
        return obj.books.count()
    get_total_books.short_description = 'Total Books'

    def get_total_pages(self, obj):
        return obj.get_total_pages()
    get_total_pages.short_description = 'Total Pages'

@admin.register(BookDetails)
class BookDetailsAdmin(admin.ModelAdmin):
    list_display = ['report', 'book_name', 'snp_pages', 'gnp_pages_count', 'total_pages']
    list_filter = ['book_name', 'report__plant_id']
    search_fields = ['report__plant_name', 'book_name']
```

## 9. Implementation Steps

### Phase 1: Models & Database (Day 1)
1. Create model classes in pagination_dash/models.py
2. Add model validation logic
3. Create initial migration: `python manage.py makemigrations pagination_dash`
4. Review migration file
5. Apply migration: `python manage.py migrate`
6. Test models in Django shell

### Phase 2: Admin Interface (Day 1)
1. Configure admin.py with inline editors
2. Register models
3. Test CRUD operations in admin
4. Verify cascading deletes

### Phase 3: Forms (Day 2)
1. Create forms.py with PaginationReportForm
2. Create GNPInformationForm
3. Create BookDetailsFormSet
4. Add form validation logic
5. Test forms in Django shell

### Phase 4: Views (Day 2-3)
1. Create PlantSelectionView
2. Create PaginationCreateView
3. Create PaginationListView
4. Create PaginationDetailView
5. Create PaginationUpdateView
6. Create PaginationDeleteView
7. Add view-level validation
8. Add permission checks (optional)

### Phase 5: URLs (Day 3)
1. Create pagination_dash/urls.py
2. Configure URL patterns
3. Update production_kpi/urls.py (already done)
4. Test URL routing

### Phase 6: Templates (Day 3-4)
1. Create base.html template
2. Create plant_selection.html
3. Create pagination_form.html (without JS)
4. Create pagination_list.html
5. Create pagination_detail.html
6. Create pagination_confirm_delete.html
7. Add basic CSS styling

### Phase 7: JavaScript (Day 4-5)
1. Create pagination_form.js
2. Implement date picker
3. Implement add/remove book functionality
4. Implement auto-calculations
5. Implement form validation
6. Test all interactive features
7. Handle edge cases

### Phase 8: Testing & Refinement (Day 5-6)
1. Create test data for multiple plants
2. Test complete CRUD workflow
3. Test validation scenarios
4. Test calculations accuracy
5. Test plant isolation (URLs)
6. Cross-browser testing
7. Mobile responsiveness testing
8. Fix bugs and refine UX

### Phase 9: Documentation (Day 6)
1. Add docstrings to models, views, forms
2. Create user guide (if needed)
3. Document URL structure for sharing
4. Create deployment checklist

## 10. Key Implementation Details

### 10.1 Plant Validation
```python
# views.py - Mixin for plant validation
class PlantValidationMixin:
    def dispatch(self, request, *args, **kwargs):
        plant_id = kwargs.get('plant_id')
        if not self.is_valid_plant(plant_id):
            messages.error(request, f"Invalid plant ID: {plant_id}")
            return redirect('pagination_home')
        return super().dispatch(request, *args, **kwargs)

    def is_valid_plant(self, plant_id):
        from upload_from_pi.plant_ids import plant_details
        return any(p['id'] == plant_id for p in plant_details)

    def get_plant_name(self):
        from upload_from_pi.plant_ids import plant_details
        plant_id = self.kwargs.get('plant_id')
        plant = next((p for p in plant_details if p['id'] == plant_id), None)
        return plant['display_name'] if plant else plant_id
```

### 10.2 Auto-Calculation in Model
```python
# models.py - BookDetails save method
def save(self, *args, **kwargs):
    # Auto-populate gnp_pages_count from type
    if self.gnp_pages_type:
        self.gnp_pages_count = self.get_gnp_page_count_from_type()

    # Auto-calculate total_pages
    self.total_pages = self.snp_pages + self.gnp_pages_count

    super().save(*args, **kwargs)

def get_gnp_page_count_from_type(self):
    type_mapping = {
        '2 Pg Jkt': 2,
        '4 Pg Jkt - 2 diff clients': 4,
        '4 Pg Vantage': 4,
        '4 Pg Power Jkt': 4,
        '8 Pg Super-pano': 8,
        '6 Pg GNP': 6,
        '8 Pg GNP': 8,
    }
    return type_mapping.get(self.gnp_pages_type, 0)
```

### 10.3 Formset Handling
```python
# views.py - CreateView form_valid
def form_valid(self, form):
    context = self.get_context_data()
    gnp_form = context['gnp_form']
    book_formset = context['book_formset']

    # Validate all forms
    if not gnp_form.is_valid() or not book_formset.is_valid():
        return self.form_invalid(form)

    # Save in transaction
    with transaction.atomic():
        # Save main report
        self.object = form.save(commit=False)
        self.object.plant_id = self.kwargs['plant_id']
        self.object.plant_name = self.get_plant_name()
        if self.request.user.is_authenticated:
            self.object.created_by = self.request.user
        self.object.save()

        # Save GNP info
        gnp_info = gnp_form.save(commit=False)
        gnp_info.report = self.object
        gnp_info.save()

        # Save books
        book_formset.instance = self.object
        book_formset.save()

    messages.success(self.request, 'Pagination report created successfully!')
    return redirect('pagination_list', plant_id=self.kwargs['plant_id'])
```

## 11. Security Considerations

### 11.1 CSRF Protection
- All forms must include {% csrf_token %}
- AJAX requests must include CSRF token in headers

### 11.2 Plant Isolation
- Validate plant_id in all views
- Ensure users can only access reports for the plant in URL
- Validate report.plant_id matches URL plant_id in edit/delete/view

### 11.3 Input Validation
- Server-side validation for all numeric fields
- Date validation (not future dates)
- Sanitize text input to prevent XSS
- Validate book name choices

### 11.4 Authentication (Optional)
- Can add login_required decorator to views
- Track created_by user
- Implement permission-based access control

## 12. Performance Optimization

### 12.1 Database Queries
- Use select_related for report.gnp_info
- Use prefetch_related for report.books
- Add database indexes on frequently queried fields
- Use pagination for list views

### 12.2 Caching (Future Enhancement)
- Cache plant_details lookup
- Cache aggregate calculations for read-only views

### 12.3 Frontend Performance
- Minify CSS/JS files
- Use CDN for common libraries (jQuery, Bootstrap)
- Lazy load JavaScript for non-critical features

## 13. Future Enhancements

### 13.1 Reporting & Analytics
- Generate PDF reports
- Export to Excel
- Date range analytics
- Plant-wise comparisons
- Trend analysis

### 13.2 Workflow Features
- Email notifications on submission
- Approval workflow
- Data validation rules
- Bulk import from CSV

### 13.3 Integration
- API endpoints for mobile app
- Integration with existing production_kpi data
- Real-time updates via WebSockets

### 13.4 User Experience
- AJAX form submission (no page reload)
- Autosave drafts
- Keyboard shortcuts
- Print-friendly views

## 14. Testing Strategy

### 14.1 Unit Tests
- Model methods (calculations, validations)
- Form validation logic
- Utility functions

### 14.2 Integration Tests
- View workflows (create → edit → delete)
- Form submission with formsets
- Database constraints

### 14.3 End-to-End Tests
- Complete user journey per plant
- Multi-plant data isolation
- Browser compatibility

### 14.4 Test Data
- Create fixtures for all 14 plants
- Sample data covering all book types
- Edge cases (empty GNP, max books, etc.)

## 15. Deployment Checklist

- [ ] Apply all migrations
- [ ] Create superuser account
- [ ] Load plant data
- [ ] Configure static files
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up production database
- [ ] Configure timezone (TIME_ZONE = 'Asia/Kolkata')
- [ ] Test all 14 plant URLs
- [ ] Verify CSRF middleware
- [ ] Set up logging
- [ ] Configure backup strategy
- [ ] Document plant-specific URLs for sharing
- [ ] Train users on the system

## 16. URL Distribution Plan

### 16.1 Plant-Specific URLs to Share

| Plant | Location | URL |
|-------|----------|-----|
| Airoli | Mumbai | `/pagination/ODBCAIR30/create/` |
| Baroda | Baroda | `/pagination/ACTIVE42/create/` |
| Bhosari | Pune | `/pagination/ODBCAIR32/create/` |
| Bommasandra | Bangalore | `/pagination/MAIN34/create/` |
| Butibori | Nagpur | `/pagination/MAIN38/create/` |
| Chemmencherry | Chennai | `/pagination/MAIN35/create/` |
| Chinhat | Lucknow | `/pagination/MAIN40/create/` |
| Kandivali | Mumbai | `/pagination/ODBCAIR28/create/` |
| Manesar | Delhi NCR | `/pagination/ACTIVE44/create/` |
| Nacharam | Hyderabad | `/pagination/MAIN36/create/` |
| Sahibabad | Delhi NCR | `/pagination/MAIN41/create/` |
| Saltlake | Kolkata | `/pagination/ODBCAIR33/create/` |
| Trivandrum | Kerala | `/pagination/ACTIVE43/create/` |
| Vejalpur | Ahmedabad | `/pagination/MAIN37/create/` |

---

## Appendix A: File Structure

```
pagination_dash/
├── __init__.py
├── admin.py                 # Admin configuration
├── apps.py
├── forms.py                 # Forms and formsets
├── models.py                # Database models
├── urls.py                  # URL routing
├── views.py                 # View classes
├── tests.py                 # Unit tests
├── migrations/
│   └── 0001_initial.py
├── static/
│   └── pagination_dash/
│       ├── css/
│       │   └── pagination_styles.css
│       └── js/
│           └── pagination_form.js
└── templates/
    └── pagination_dash/
        ├── base.html
        ├── plant_selection.html
        ├── pagination_form.html
        ├── pagination_list.html
        ├── pagination_detail.html
        └── pagination_confirm_delete.html
```

## Appendix B: Model Field Mapping to Form

| Form Element | Model | Field | Notes |
|--------------|-------|-------|-------|
| Issue Date | PaginationReport | issue_date | DateField with picker |
| Book Name (Row 1) | BookDetails | book_name | Default: TOI B-1 |
| Book Name (Row 2) | BookDetails | book_name | Default: TOI B-2 |
| Book Name (Row 3) | BookDetails | book_name | Default: BT B-1 |
| SNP Pages | BookDetails | snp_pages | Numeric input |
| GNP Pages (Type) | BookDetails | gnp_pages_type | Select dropdown |
| GNP Pages (Count) | BookDetails | gnp_pages_count | Auto-calculated |
| Total Pages | BookDetails | total_pages | Auto-calculated |
| No. of GNP Jackets | BookDetails | number_of_gnp_jackets | Numeric input |
| ET Checkbox | GNPInformation | et | Boolean |
| MT Checkbox | GNPInformation | mt | Boolean |
| Mirror Checkbox | GNPInformation | mirror | Boolean |
| NBT Checkbox | GNPInformation | nbt | Boolean |
| GNP Remarks | GNPInformation | remarks | Textarea |
| TOI Remarks | PaginationReport | remarks_toi | Textarea |
| Others Remarks | PaginationReport | remarks_others | Textarea |
| First Time Execution | PaginationReport | first_time_execution_info | Textarea |

---

**Document Version**: 1.0
**Last Updated**: 2025-10-06
**Author**: Generated by Claude Code
**Status**: Ready for Implementation
