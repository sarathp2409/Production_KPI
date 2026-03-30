from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import PaginationReport, GNPInformation, BookDetails, CompetitorData, CompetitorBookDetails
from .utils import get_competitor_choices_for_plant
from .gnp_config import get_gnp_field_names_for_plant


class PaginationReportForm(forms.ModelForm):
    """
    Main form for PaginationReport with date validation and custom widgets
    """

    class Meta:
        model = PaginationReport
        fields = [
            'plant_id',
            'plant_name',
            'issue_date',
            'remarks_toi',
            'remarks_others',
            'first_time_execution_info',
            'auto_collated_groups'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Select issue date'
            }),
            'remarks_toi': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Enter remarks for TOI publications...'
            }),
            'remarks_others': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Enter remarks for other publications...'
            }),
            'first_time_execution_info': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'First time execution information (if any)...'
            }),
            'plant_id': forms.HiddenInput(),
            'plant_name': forms.HiddenInput(),
            'auto_collated_groups': forms.HiddenInput(),
        }
        labels = {
            'issue_date': 'Issue Date',
            'remarks_toi': 'TOI',
            'remarks_others': 'Other Editions',
            'first_time_execution_info': 'First Time Execution Info',
            'auto_collated_groups': 'Auto Collated Groups'
        }

    def clean(self):
        """
        Additional validation for the entire form
        """
        cleaned_data = super().clean()
        plant_id = cleaned_data.get('plant_id')
        plant_name = cleaned_data.get('plant_name')
        issue_date = cleaned_data.get('issue_date')
        auto_collated_groups = cleaned_data.get('auto_collated_groups')

        # Check for duplicate plant_id + issue_date combination (for create)
        if plant_id and issue_date and not self.instance.pk:
            if PaginationReport.objects.filter(plant_id=plant_id, issue_date=issue_date).exists():
                raise ValidationError(
                    f'A report for {plant_name} on {issue_date} already exists.'
                )

        if not auto_collated_groups:
            cleaned_data['auto_collated_groups'] = []

        return cleaned_data


class GNPInformationForm(forms.ModelForm):
    """
    Form for GNP Information with checkboxes and remarks
    Dynamically shows only relevant publications based on plant location
    """

    class Meta:
        model = GNPInformation
        fields = ['et', 'et_b1', 'et_b2', 'mt', 'mirror', 'nbt', 'tims', 'et_had_2_books', 'remarks']
        widgets = {
            'et': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500',
                'id': 'id_gnp-et'
            }),
            'et_b1': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500',
                'id': 'id_gnp-et_b1'
            }),
            'et_b2': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500',
                'id': 'id_gnp-et_b2'
            }),
            'mt': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500'
            }),
            'mirror': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500'
            }),
            'nbt': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500'
            }),
            'tims': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500'
            }),
            'et_had_2_books': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500',
                'id': 'id_gnp-et_had_2_books'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Enter GNP-specific remarks...'
            }),
        }
        labels = {
            'et': 'ET (Economic Times)',
            'et_b1': 'ET B-1',
            'et_b2': 'ET B-2',
            'mt': 'MT (Maharashtra Times)',
            'mirror': 'Mirror',
            'nbt': 'NBT (Navbharat Times)',
            'tims': 'TIMS',
            'et_had_2_books': 'ET had 2 Books',
            'remarks': 'GNP Remarks'
        }

    def __init__(self, *args, plant_name=None, **kwargs):
        """
        Initialize form and filter fields based on plant location

        Args:
            plant_name: Name of the plant to determine which publications to show
        """
        super().__init__(*args, **kwargs)

        # Store plant_name for template access
        self.plant_name = plant_name

        # If plant_name is provided, get the list of allowed publications
        if plant_name:
            allowed_fields = get_gnp_field_names_for_plant(plant_name)

            # List of all publication fields (including ET variants)
            all_pub_fields = ['et', 'et_b1', 'et_b2', 'mt', 'mirror', 'nbt', 'tims', 'et_had_2_books']

            # Hide fields that are not in the allowed list
            for field_name in all_pub_fields:
                if field_name not in allowed_fields:
                    # Remove field from form
                    if field_name in self.fields:
                        del self.fields[field_name]


class BookDetailsForm(forms.ModelForm):
    """
    Form for individual Book Details with auto-calculation support
    """

    # Override fields to make auto-calculated ones optional
    snp_pages = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent snp-pages-input',
            'min': '0',
            'value': '0'
        })
    )
    gnp_pages_count = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 gnp-count-input',
            'readonly': 'readonly',
            'placeholder': '0'
        })
    )
    total_pages = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 total-pages-input',
            'readonly': 'readonly',
            'placeholder': '0'
        })
    )
    number_of_gnp_jackets = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent gnp-jackets-input',
            'min': '0',
            'value': '0'
        })
    )

    class Meta:
        model = BookDetails
        fields = ['book_name', 'snp_pages', 'gnp_pages_type', 'gnp_pages_count', 'total_pages', 'number_of_gnp_jackets', 'balloon_printed', 'has_masthead', 'order']
        widgets = {
            'book_name': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent book-name-select',
                'required': False
            }),
            'gnp_pages_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent gnp-type-select',
                'required': False
            }),
            'balloon_printed': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 balloon-printed-checkbox'
            }),
            'has_masthead': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 has-masthead-checkbox'
            }),
            'order': forms.HiddenInput(),
        }
        labels = {
            'book_name': 'Book Name',
            'snp_pages': 'SNP Pages',
            'gnp_pages_type': 'GNP Pages',
            'gnp_pages_count': 'GNP Count',
            'total_pages': 'Total Pages',
            'number_of_gnp_jackets': 'No. of GNP Jackets',
            'balloon_printed': 'Balloon Printed',
            'has_masthead': 'Has Masthead'
        }

    def clean(self):
        """
        Validate book details and auto-calculate fields
        """
        cleaned_data = super().clean()
        book_name = cleaned_data.get('book_name')
        snp_pages = cleaned_data.get('snp_pages') or 0
        gnp_pages_type = cleaned_data.get('gnp_pages_type')
        number_of_gnp_jackets = cleaned_data.get('number_of_gnp_jackets') or 0

        # Ensure default values for auto-calculated fields
        if 'gnp_pages_count' not in cleaned_data or cleaned_data['gnp_pages_count'] is None:
            cleaned_data['gnp_pages_count'] = 0
        if 'total_pages' not in cleaned_data or cleaned_data['total_pages'] is None:
            cleaned_data['total_pages'] = 0

        # Only validate if book_name is provided (row is being used)
        if book_name:
            # Auto-calculate gnp_pages_count from type
            if gnp_pages_type:
                gnp_pages_count = BookDetails.GNP_TYPE_PAGE_MAPPING.get(gnp_pages_type, 0)
                cleaned_data['gnp_pages_count'] = gnp_pages_count
            else:
                cleaned_data['gnp_pages_count'] = 0

            # Auto-calculate total_pages
            cleaned_data['total_pages'] = snp_pages + cleaned_data['gnp_pages_count']

            # Warning: If GNP type is selected, jacket count should be > 0
            if gnp_pages_type and number_of_gnp_jackets == 0:
                # This is a warning, not an error - we'll add a message in the view
                pass

        return cleaned_data


# Custom formset class for BookDetails with duplicate validation
class BaseBookDetailsFormSet(forms.BaseInlineFormSet):
    """
    Custom formset to validate no duplicate book names within the same submission
    """
    def clean(self):
        """
        Check that no two forms have the same book name
        """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        book_names = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                book_name = form.cleaned_data.get('book_name')
                if book_name:
                    if book_name in book_names:
                        raise ValidationError(
                            f'Duplicate book name detected: "{book_name}". Each book name can only appear once.',
                            code='duplicate_book'
                        )
                    book_names.append(book_name)


# Create inline formset for BookDetails
BookDetailsFormSet = inlineformset_factory(
    PaginationReport,
    BookDetails,
    form=BookDetailsForm,
    formset=BaseBookDetailsFormSet,  # Use custom formset class
    extra=3,  # 3 default rows
    can_delete=True,
    min_num=1,  # At least one book is required
    validate_min=True,
    max_num=10,  # Maximum 10 books
    validate_max=True,
)


class BookDetailsFormSetHelper:
    """
    Helper class to manage BookDetails formset with default values
    """

    DEFAULT_BOOKS = [
        {'book_name': 'TOI B-1', 'order': 1},
        {'book_name': 'TOI B-2', 'order': 2},
        {'book_name': 'TIMS B-1', 'order': 3},
    ]

    ADDITIONAL_BOOK_CHOICES = [
        'TIMS B-2',
        'TOI Supp-1',
        'TOI Supp-2',
        'TOI Supp-3',
    ]

    @classmethod
    def get_initial_data(cls):
        """
        Get initial data for formset with 3 default books
        """
        return cls.DEFAULT_BOOKS

    @classmethod
    def get_book_choices_for_row(cls, row_index, selected_books):
        """
        Get available book name choices based on row index and already selected books

        Args:
            row_index: Index of the current row (0-based)
            selected_books: List of already selected book names

        Returns:
            List of tuples for choices
        """
        all_choices = [choice[0] for choice in BookDetails.BOOK_NAME_CHOICES]

        # For first 3 rows, limit to default books
        if row_index < 3:
            available = [book['book_name'] for book in cls.DEFAULT_BOOKS]
        else:
            # For additional rows, show additional book choices
            available = cls.ADDITIONAL_BOOK_CHOICES

        # Filter out already selected books (except for current row)
        # This will be handled in JavaScript for better UX

        return [(choice, choice) for choice in all_choices if choice in available]


class CompetitorDataForm(forms.ModelForm):
    """
    Form for competitor data (simplified - book details handled separately)
    """

    # Innovation multi-select field with checkboxes
    innovation = forms.TypedMultipleChoiceField(
        required=False,
        choices=CompetitorData.INNOVATION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'comp-innovation-checkbox'
        }),
        label='Innovation',
        coerce=str,
        empty_value=[]
    )

    class Meta:
        model = CompetitorData
        fields = ['competitor_name', 'innovation', 'comment']
        widgets = {
            'competitor_name': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent comp-name-select',
                'required': False
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Comments...',
                'required': False
            }),
        }
        labels = {
            'competitor_name': 'Competitor Name',
            'innovation': 'Innovation',
            'comment': 'Comment'
        }

    def __init__(self, *args, plant_id=None, plant_name=None, **kwargs):
        """
        Initialize form with dynamic competitor choices based on plant
        """
        super().__init__(*args, **kwargs)

        # Set competitor choices based on plant
        if plant_id or plant_name:
            competitor_choices = get_competitor_choices_for_plant(plant_id, plant_name)
            if competitor_choices:
                # Add empty option at the beginning
                self.fields['competitor_name'].widget.choices = [('', '--- Select Competitor ---')] + competitor_choices

        # Pre-populate innovation field if instance has data
        if self.instance and self.instance.pk and self.instance.innovation:
            self.initial['innovation'] = self.instance.innovation

    def clean_innovation(self):
        """
        Convert MultipleChoiceField list to JSON-compatible list
        Filter out any empty strings or None values
        """
        innovation = self.cleaned_data.get('innovation')
        if innovation:
            # Filter out empty strings and None values, return as list
            filtered = [item for item in innovation if item and item.strip()]
            return filtered if filtered else []
        return []


class CompetitorBookDetailsForm(forms.ModelForm):
    """
    Form for competitor book details with auto-calculation support
    Similar to BookDetailsForm but for competitor data
    """

    # Override fields for auto-calculation
    snp_pages = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent comp-book-snp-input',
            'min': '0',
            'value': '0'
        })
    )
    gnp_pages_count = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 comp-book-gnp-count-input',
            'readonly': 'readonly',
            'placeholder': '0'
        })
    )
    total_pages = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 comp-book-total-input',
            'readonly': 'readonly',
            'placeholder': '0'
        })
    )
    number_of_gnp_jacket = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent comp-book-gnp-jacket-input',
            'min': '0',
            'value': '0'
        })
    )
    number_of_books = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent comp-book-books-input',
            'min': '0',
            'value': '0'
        })
    )

    class Meta:
        model = CompetitorBookDetails
        fields = ['book_type', 'snp_pages', 'gnp_pages_type', 'gnp_pages_count', 'total_pages', 'number_of_gnp_jacket', 'number_of_books']
        widgets = {
            'book_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 comp-book-type-select',
                'readonly': 'readonly'
            }),
            'gnp_pages_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent comp-book-gnp-type-select',
                'required': False
            }),
        }
        labels = {
            'book_type': 'Book Type',
            'snp_pages': 'SNP Pages',
            'gnp_pages_type': 'GNP Type',
            'gnp_pages_count': 'GNP Count',
            'total_pages': 'Total Pages',
            'number_of_gnp_jacket': 'No. of GNP Jacket',
            'number_of_books': 'No. of Books'
        }

    def clean(self):
        """
        Validate and auto-calculate fields
        """
        cleaned_data = super().clean()
        book_type = cleaned_data.get('book_type')
        snp_pages = cleaned_data.get('snp_pages') or 0
        gnp_pages_type = cleaned_data.get('gnp_pages_type')

        # Ensure default values for auto-calculated fields
        if 'gnp_pages_count' not in cleaned_data or cleaned_data['gnp_pages_count'] is None:
            cleaned_data['gnp_pages_count'] = 0
        if 'total_pages' not in cleaned_data or cleaned_data['total_pages'] is None:
            cleaned_data['total_pages'] = 0

        # Only validate if book_type is provided (form is being used)
        if book_type:
            # Auto-calculate gnp_pages_count from type
            if gnp_pages_type:
                from .models import BookDetails
                gnp_pages_count = BookDetails.GNP_TYPE_PAGE_MAPPING.get(gnp_pages_type, 0)
                cleaned_data['gnp_pages_count'] = gnp_pages_count
            else:
                cleaned_data['gnp_pages_count'] = 0

            # Auto-calculate total_pages
            cleaned_data['total_pages'] = snp_pages + cleaned_data['gnp_pages_count']

        return cleaned_data


# Create inline formset for CompetitorBookDetails
CompetitorBookDetailsFormSet = inlineformset_factory(
    CompetitorData,
    CompetitorBookDetails,
    form=CompetitorBookDetailsForm,
    extra=2,  # 2 default forms for Main and Supplement
    can_delete=False,  # Cannot delete, always need both book types
    min_num=0,  # Don't require minimum since parent competitor might be empty
    max_num=2,  # Maximum 2 book types
    validate_min=False,
    validate_max=True,
)


# Custom formset class for CompetitorData with duplicate validation
class BaseCompetitorDataFormSet(forms.BaseInlineFormSet):
    """
    Custom formset to validate no duplicate competitor names within the same submission
    """
    def clean(self):
        """
        Check that no two forms have the same competitor name
        """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        competitor_names = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                competitor_name = form.cleaned_data.get('competitor_name')
                if competitor_name:
                    if competitor_name in competitor_names:
                        raise ValidationError(
                            f'Duplicate competitor name detected: "{competitor_name}". Each competitor can only appear once.',
                            code='duplicate_competitor'
                        )
                    competitor_names.append(competitor_name)


# Create inline formset for CompetitorData
CompetitorDataFormSet = inlineformset_factory(
    PaginationReport,
    CompetitorData,
    form=CompetitorDataForm,
    formset=BaseCompetitorDataFormSet,  # Use custom formset class
    extra=2,  # 2 default rows for competitors
    can_delete=True,
    min_num=0,  # Competitors are optional
    validate_min=False,
    max_num=10,  # Maximum 10 competitors
    validate_max=True,
)


class CombinedPaginationForm:
    """
    Helper class to combine all forms together for easier handling in views
    Handles 3-level nesting: Report → Competitors → Competitor Books
    """

    def __init__(self, data=None, instance=None, plant_id=None, plant_name=None):
        self.plant_id = plant_id
        self.plant_name = plant_name
        self.data = data

        # Initialize main report form
        initial_data = {}
        if plant_id and plant_name and not instance:
            initial_data = {
                'plant_id': plant_id,
                'plant_name': plant_name
            }

        self.report_form = PaginationReportForm(
            data=data,
            instance=instance,
            initial=initial_data
        )

        # Initialize GNP form
        gnp_instance = None
        if instance and hasattr(instance, 'gnp_info'):
            gnp_instance = instance.gnp_info

        self.gnp_form = GNPInformationForm(
            data=data,
            instance=gnp_instance,
            prefix='gnp',
            plant_name=plant_name
        )

        # Initialize book formset
        formset_initial = None if instance else BookDetailsFormSetHelper.get_initial_data()

        self.book_formset = BookDetailsFormSet(
            data=data,
            instance=instance,
            initial=formset_initial,
            prefix='books'
        )

        # Initialize competitor formset
        self.competitor_formset = CompetitorDataFormSet(
            data=data,
            instance=instance,
            prefix='competitors',
            form_kwargs={'plant_id': plant_id, 'plant_name': plant_name}
        )

        # Initialize nested book formsets for each competitor
        self.competitor_book_formsets = {}
        if instance and data:
            # For update with POST data, we need to handle both existing and new competitors
            # Check the TOTAL_FORMS from POST data to see how many competitor forms were submitted
            management_form_key = 'competitors-TOTAL_FORMS'
            if management_form_key in data:
                total_forms = int(data[management_form_key])
                existing_competitors = list(instance.competitors.all())

                # Create a mapping of existing competitors by their form position
                existing_competitor_map = {idx: comp for idx, comp in enumerate(existing_competitors)}

                # Create book formsets for all forms (existing and new)
                for idx in range(total_forms):
                    formset_prefix = f'competitors-{idx}-books'

                    # If this index corresponds to an existing competitor, use its instance
                    if idx in existing_competitor_map:
                        self.competitor_book_formsets[idx] = CompetitorBookDetailsFormSet(
                            data=data,
                            instance=existing_competitor_map[idx],
                            prefix=formset_prefix
                        )
                    else:
                        # New competitor or empty form
                        book_initial = [
                            {'book_type': 'Main'},
                            {'book_type': 'Supplement'}
                        ]
                        self.competitor_book_formsets[idx] = CompetitorBookDetailsFormSet(
                            data=data,
                            prefix=formset_prefix,
                            initial=book_initial
                        )
        elif instance:
            # For existing instance on GET request (no POST data)
            existing_competitors = list(instance.competitors.all())
            for idx, competitor in enumerate(existing_competitors):
                formset_prefix = f'competitors-{idx}-books'
                self.competitor_book_formsets[idx] = CompetitorBookDetailsFormSet(
                    data=data,
                    instance=competitor,
                    prefix=formset_prefix
                )

            # Also create book formsets for the extra empty forms
            # The competitor formset has extra=2, so we need to initialize book formsets for those
            num_existing = len(existing_competitors)
            num_extra = 2  # This should match CompetitorDataFormSet's extra parameter
            for idx in range(num_existing, num_existing + num_extra):
                formset_prefix = f'competitors-{idx}-books'
                book_initial = [
                    {'book_type': 'Main'},
                    {'book_type': 'Supplement'}
                ]
                self.competitor_book_formsets[idx] = CompetitorBookDetailsFormSet(
                    data=data,
                    prefix=formset_prefix,
                    initial=book_initial
                )
        elif data:
            # For POST data, determine how many competitor forms exist
            management_form_key = 'competitors-TOTAL_FORMS'
            if management_form_key in data:
                total_forms = int(data[management_form_key])
                for idx in range(total_forms):
                    formset_prefix = f'competitors-{idx}-books'
                    # Create formset without instance for new competitors
                    book_initial = [
                        {'book_type': 'Main'},
                        {'book_type': 'Supplement'}
                    ]
                    self.competitor_book_formsets[idx] = CompetitorBookDetailsFormSet(
                        data=data,
                        prefix=formset_prefix,
                        initial=book_initial
                    )
        else:
            # For new form, create book formsets for default competitors (2)
            for idx in range(2):
                formset_prefix = f'competitors-{idx}-books'
                book_initial = [
                    {'book_type': 'Main'},
                    {'book_type': 'Supplement'}
                ]
                self.competitor_book_formsets[idx] = CompetitorBookDetailsFormSet(
                    prefix=formset_prefix,
                    initial=book_initial
                )

    def is_valid(self):
        """
        Validate all forms including nested competitor book formsets
        """
        report_valid = self.report_form.is_valid()
        gnp_valid = self.gnp_form.is_valid()
        formset_valid = self.book_formset.is_valid()
        competitor_valid = self.competitor_formset.is_valid()

        # Validate nested competitor book formsets
        # Only validate book formsets for competitors that have data and aren't marked for deletion
        competitor_books_valid = True
        for idx, book_formset in self.competitor_book_formsets.items():
            # Check if this competitor form has data
            if idx < len(self.competitor_formset.forms):
                competitor_form = self.competitor_formset.forms[idx]
                # Only validate if competitor has a name and isn't marked for deletion
                if (competitor_form.cleaned_data if hasattr(competitor_form, 'cleaned_data') else None) and \
                   competitor_form.cleaned_data.get('competitor_name') and \
                   not competitor_form.cleaned_data.get('DELETE'):
                    # Just validate that the book formset is valid (allows all zeros)
                    if not book_formset.is_valid():
                        competitor_books_valid = False

        # Additional cross-form validation
        if report_valid and formset_valid:
            # Check that at least one book has data
            has_valid_book = False
            for form in self.book_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    if form.cleaned_data.get('book_name'):
                        has_valid_book = True
                        break

            if not has_valid_book:
                self.book_formset._non_form_errors = self.book_formset.error_class([
                    'At least one book entry is required.'
                ])
                formset_valid = False
            else:
                selected_books = self._get_selected_book_names()
                self._normalized_auto_collated_groups = self._normalize_auto_collated_groups(
                    self.report_form.cleaned_data.get('auto_collated_groups'),
                    selected_books
                )
                self.report_form.cleaned_data['auto_collated_groups'] = self._normalized_auto_collated_groups

        return report_valid and gnp_valid and formset_valid and competitor_valid and competitor_books_valid

    def _get_selected_book_names(self):
        """
        Collect selected book names from the book formset in form order.
        """
        book_names = []
        for form in self.book_formset:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                book_name = form.cleaned_data.get('book_name')
                if book_name and book_name not in book_names:
                    book_names.append(book_name)
        return book_names

    def _normalize_auto_collated_groups(self, groups, selected_books):
        """
        Normalize auto-collated groups to a list of lists of valid book names.
        """
        if not groups or not isinstance(groups, list):
            return []

        selected_set = set(selected_books)
        normalized_groups = []
        for group in groups:
            if not isinstance(group, (list, tuple)):
                continue

            cleaned_group = []
            seen = set()
            for name in group:
                if not isinstance(name, str):
                    continue
                name = name.strip()
                if name and name in selected_set and name not in seen:
                    cleaned_group.append(name)
                    seen.add(name)

            if cleaned_group:
                normalized_groups.append(cleaned_group)

        return normalized_groups

    def save(self, commit=True):
        """
        Save all forms together in a transaction including nested competitor books
        """
        from django.db import transaction

        if not commit:
            raise ValueError('CombinedPaginationForm only supports commit=True')

        with transaction.atomic():
            # Save main report
            if hasattr(self, '_normalized_auto_collated_groups'):
                self.report_form.instance.auto_collated_groups = self._normalized_auto_collated_groups
            else:
                self.report_form.instance.auto_collated_groups = (
                    self.report_form.cleaned_data.get('auto_collated_groups') or []
                )

            report = self.report_form.save(commit=True)

            # Save GNP info
            gnp = self.gnp_form.save(commit=False)
            gnp.report = report
            gnp.save()

            # Save books
            self.book_formset.instance = report
            self.book_formset.save()

            # Save competitors and their nested books
            self.competitor_formset.instance = report
            competitors = self.competitor_formset.save(commit=True)

            # Now save the nested book formsets for each competitor
            # Match saved competitors with their book formsets by ACTUAL form index (not enumerate)
            for form_idx, competitor_form in enumerate(self.competitor_formset.forms):
                # Skip if form has no data or is marked for deletion
                if not (competitor_form.cleaned_data and not competitor_form.cleaned_data.get('DELETE')):
                    continue

                # Skip if no competitor name (empty form)
                if not competitor_form.cleaned_data.get('competitor_name'):
                    continue

                # Only process if competitor instance was saved
                if competitor_form.instance and competitor_form.instance.pk:
                    # Get the corresponding book formset using the ACTUAL form index
                    if form_idx in self.competitor_book_formsets:
                        book_formset = self.competitor_book_formsets[form_idx]
                        book_formset.instance = competitor_form.instance

                        # Save book formset (allows all zeros for Supplement)
                        saved_books = book_formset.save(commit=True)

                        # Ensure both Main and Supplement exist (create with zeros if missing)
                        # Check all existing books in database (not just saved ones)
                        existing_books = CompetitorBookDetails.objects.filter(
                            competitor=competitor_form.instance
                        )
                        existing_types = [book.book_type for book in existing_books]

                        if 'Main' not in existing_types:
                            CompetitorBookDetails.objects.create(
                                competitor=competitor_form.instance,
                                book_type='Main',
                                snp_pages=0,
                                gnp_pages_count=0,
                                total_pages=0,
                                number_of_gnp_jacket=0,
                                number_of_books=0
                            )

                        if 'Supplement' not in existing_types:
                            CompetitorBookDetails.objects.create(
                                competitor=competitor_form.instance,
                                book_type='Supplement',
                                snp_pages=0,
                                gnp_pages_count=0,
                                total_pages=0,
                                number_of_gnp_jacket=0,
                                number_of_books=0
                            )

        return report

    def get_errors(self):
        """
        Get all errors from all forms including nested formsets
        """
        errors = {}

        if self.report_form.errors:
            errors['report'] = self.report_form.errors

        if self.gnp_form.errors:
            errors['gnp'] = self.gnp_form.errors

        if self.book_formset.errors:
            errors['books'] = self.book_formset.errors

        if hasattr(self.book_formset, '_non_form_errors') and self.book_formset._non_form_errors:
            errors['books_general'] = self.book_formset._non_form_errors

        if self.competitor_formset.errors:
            errors['competitors'] = self.competitor_formset.errors

        if hasattr(self.competitor_formset, '_non_form_errors') and self.competitor_formset._non_form_errors:
            errors['competitors_general'] = self.competitor_formset._non_form_errors

        # Add nested book formset errors
        for idx, book_formset in self.competitor_book_formsets.items():
            if book_formset.errors:
                errors[f'competitor_{idx}_books'] = book_formset.errors

        return errors
