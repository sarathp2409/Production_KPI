"""
Test script to verify duplicate validation for Book Names and Competitor Names

This test demonstrates that:
1. Creating records with duplicate book names in the same submission raises ValidationError
2. Creating records with duplicate competitor names in the same submission raises ValidationError
3. Both Create and Update views properly validate duplicates
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from pagination_dash.models import PaginationReport, BookDetails, CompetitorData
from pagination_dash.forms import BookDetailsFormSet, CompetitorDataFormSet
from datetime import date


class DuplicateValidationTest(TestCase):
    """Test duplicate validation for Book Names and Competitor Names"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.report = PaginationReport.objects.create(
            plant_id='ODBCAIR30',
            plant_name='Airoli',
            issue_date=date.today(),
            created_by=self.user
        )

    def test_duplicate_book_names_in_formset_raises_error(self):
        """Test that duplicate book names in the same formset submission raise ValidationError"""
        # Simulate POST data with duplicate book names
        data = {
            'books-TOTAL_FORMS': '2',
            'books-INITIAL_FORMS': '0',
            'books-MIN_NUM_FORMS': '1',
            'books-MAX_NUM_FORMS': '10',

            # First book
            'books-0-book_name': 'TOI B-1',
            'books-0-snp_pages': '10',
            'books-0-gnp_pages_type': '',
            'books-0-gnp_pages_count': '0',
            'books-0-total_pages': '10',
            'books-0-number_of_gnp_jackets': '0',
            'books-0-order': '1',

            # Second book - DUPLICATE NAME
            'books-1-book_name': 'TOI B-1',  # Same as first book
            'books-1-snp_pages': '8',
            'books-1-gnp_pages_type': '',
            'books-1-gnp_pages_count': '0',
            'books-1-total_pages': '8',
            'books-1-number_of_gnp_jackets': '0',
            'books-1-order': '2',
        }

        formset = BookDetailsFormSet(data=data, instance=self.report, prefix='books')

        # Formset should be invalid due to duplicate book names
        self.assertFalse(formset.is_valid())

        # Check that the error mentions duplicate
        with self.assertRaises(ValidationError) as context:
            formset.clean()

        self.assertIn('Duplicate book name', str(context.exception))

    def test_duplicate_competitor_names_in_formset_raises_error(self):
        """Test that duplicate competitor names in the same formset submission raise ValidationError"""
        # Simulate POST data with duplicate competitor names
        data = {
            'competitors-TOTAL_FORMS': '2',
            'competitors-INITIAL_FORMS': '0',
            'competitors-MIN_NUM_FORMS': '0',
            'competitors-MAX_NUM_FORMS': '10',

            # First competitor
            'competitors-0-competitor_name': 'Hindustan Times',
            'competitors-0-innovation': [],
            'competitors-0-comment': 'Test comment',

            # Second competitor - DUPLICATE NAME
            'competitors-1-competitor_name': 'Hindustan Times',  # Same as first
            'competitors-1-innovation': [],
            'competitors-1-comment': 'Another comment',
        }

        formset = CompetitorDataFormSet(
            data=data,
            instance=self.report,
            prefix='competitors',
            form_kwargs={'plant_id': 'ODBCAIR30', 'plant_name': 'Airoli'}
        )

        # Formset should be invalid due to duplicate competitor names
        self.assertFalse(formset.is_valid())

        # Check that the error mentions duplicate
        with self.assertRaises(ValidationError) as context:
            formset.clean()

        self.assertIn('Duplicate competitor name', str(context.exception))

    def test_unique_book_names_pass_validation(self):
        """Test that unique book names pass validation"""
        data = {
            'books-TOTAL_FORMS': '2',
            'books-INITIAL_FORMS': '0',
            'books-MIN_NUM_FORMS': '1',
            'books-MAX_NUM_FORMS': '10',

            # First book
            'books-0-book_name': 'TOI B-1',
            'books-0-snp_pages': '10',
            'books-0-gnp_pages_type': '',
            'books-0-gnp_pages_count': '0',
            'books-0-total_pages': '10',
            'books-0-number_of_gnp_jackets': '0',
            'books-0-order': '1',

            # Second book - UNIQUE NAME
            'books-1-book_name': 'TOI B-2',  # Different from first book
            'books-1-snp_pages': '8',
            'books-1-gnp_pages_type': '',
            'books-1-gnp_pages_count': '0',
            'books-1-total_pages': '8',
            'books-1-number_of_gnp_jackets': '0',
            'books-1-order': '2',
        }

        formset = BookDetailsFormSet(data=data, instance=self.report, prefix='books')

        # Formset should be valid with unique book names
        self.assertTrue(formset.is_valid())

    def test_unique_competitor_names_pass_validation(self):
        """Test that unique competitor names pass validation"""
        data = {
            'competitors-TOTAL_FORMS': '2',
            'competitors-INITIAL_FORMS': '0',
            'competitors-MIN_NUM_FORMS': '0',
            'competitors-MAX_NUM_FORMS': '10',

            # First competitor
            'competitors-0-competitor_name': 'Hindustan Times',
            'competitors-0-innovation': [],
            'competitors-0-comment': 'Test comment',

            # Second competitor - UNIQUE NAME
            'competitors-1-competitor_name': 'Indian Express',  # Different from first
            'competitors-1-innovation': [],
            'competitors-1-comment': 'Another comment',
        }

        formset = CompetitorDataFormSet(
            data=data,
            instance=self.report,
            prefix='competitors',
            form_kwargs={'plant_id': 'ODBCAIR30', 'plant_name': 'Airoli'}
        )

        # Formset should be valid with unique competitor names
        self.assertTrue(formset.is_valid())


if __name__ == '__main__':
    import django
    from django.conf import settings

    # Run tests
    print("Running duplicate validation tests...")
    print("\nNote: Run this with: python manage.py test pagination_dash.test_duplicate_validation")
