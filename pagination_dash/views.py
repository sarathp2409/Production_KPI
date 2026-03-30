from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.db.models import Q, Sum, Count

from .models import PaginationReport, GNPInformation, BookDetails, UserProfile
from .forms import CombinedPaginationForm
from .gnp_config import has_gnp_publications, get_publication_display_info


class PlantPermissionMixin:
    """
    Mixin to enforce plant-based access control.
    Ensures users can only access plants they're authorized for.
    """

    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission to access this plant"""
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())

        plant_id = kwargs.get('plant_id')

        if plant_id:
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)

            # Check if user has access to this plant
            if not profile.has_plant_access(plant_id):
                raise PermissionDenied(
                    f"You do not have permission to access {plant_id}. "
                    f"Please contact your administrator."
                )

        return super().dispatch(request, *args, **kwargs)


class PlantValidationMixin:
    """
    Mixin to validate plant_id against plant_details and provide plant information
    """

    def dispatch(self, request, *args, **kwargs):
        """Validate plant_id before processing request"""
        plant_id = kwargs.get('plant_id')

        if plant_id and not self.is_valid_plant(plant_id):
            messages.error(request, f"Invalid plant ID: {plant_id}")
            return redirect('pagination_dash:pagination_home')

        return super().dispatch(request, *args, **kwargs)

    def is_valid_plant(self, plant_id):
        """Check if plant_id exists in plant_details"""
        from upload_from_pi.plant_ids import plant_details
        return any(p['id'] == plant_id for p in plant_details)

    def get_plant_details(self, plant_id):
        """Get plant details dictionary for given plant_id"""
        from upload_from_pi.plant_ids import plant_details
        return next((p for p in plant_details if p['id'] == plant_id), None)

    def get_plant_name(self):
        """Get plant display name from URL kwargs"""
        plant_id = self.kwargs.get('plant_id')
        plant = self.get_plant_details(plant_id)
        return plant['display_name'] if plant else plant_id

    def get_context_data(self, **kwargs):
        """Add plant information to context"""
        context = super().get_context_data(**kwargs)
        plant_id = self.kwargs.get('plant_id')

        if plant_id:
            plant = self.get_plant_details(plant_id)
            context['plant_id'] = plant_id
            context['plant_name'] = plant['display_name'] if plant else plant_id
            context['plant_details'] = plant

        return context


class PlantSelectionView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Landing page displaying all 14 plants with links to create/list views.
    RESTRICTED TO ADMIN USERS ONLY.
    """
    template_name = 'pagination_dash/plant_selection.html'
    login_url = '/accounts/login/'
    raise_exception = True

    def test_func(self):
        """Only allow admin users (staff, superuser, or plant_admin)"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return True

        # Check if user has plant_admin profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile.is_plant_admin

    def handle_no_permission(self):
        """Redirect non-admin users to their first assigned plant"""
        if self.request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            accessible_plants = profile.get_accessible_plants()

            if accessible_plants:
                # Redirect to the first plant's list view (without message)
                return redirect('pagination_dash:pagination_list', plant_id=accessible_plants[0])
            else:
                messages.error(
                    self.request,
                    "You don't have access to any plants. Please contact your administrator."
                )
                return redirect('/admin/')

        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Import plant details
        from upload_from_pi.plant_ids import plant_details

        # Sort plant details by name
        sorted_plants = sorted(plant_details, key=lambda x: x.get('name', ''))

        # Get report counts for each plant
        plants_with_counts = []
        for plant in sorted_plants:
            report_count = PaginationReport.objects.filter(plant_id=plant['id']).count()
            plant_info = plant.copy()
            plant_info['report_count'] = report_count
            plants_with_counts.append(plant_info)

        context['plants'] = plants_with_counts
        context['is_admin'] = True
        return context


class PaginationCreateView(PlantPermissionMixin, PlantValidationMixin, CreateView):
    """
    Create new pagination report for a specific plant
    """
    model = PaginationReport
    template_name = 'pagination_dash/pagination_form.html'
    fields = []  # Required by CreateView, but we use CombinedPaginationForm instead

    def get_success_url(self):
        """Redirect to list view after successful creation"""
        return reverse('pagination_dash:pagination_list', kwargs={'plant_id': self.kwargs['plant_id']})

    def get_context_data(self, **kwargs):
        """Add combined form to context"""
        context = super().get_context_data(**kwargs)

        plant_id = self.kwargs['plant_id']
        plant_name = self.get_plant_name()

        if self.request.POST:
            context['combined_form'] = CombinedPaginationForm(
                data=self.request.POST,
                plant_id=plant_id,
                plant_name=plant_name
            )
        else:
            context['combined_form'] = CombinedPaginationForm(
                plant_id=plant_id,
                plant_name=plant_name
            )

        context['action'] = 'Create'
        context['submit_text'] = 'Submit'

        # Add GNP configuration
        context['has_gnp'] = has_gnp_publications(plant_name)
        context['gnp_publications'] = get_publication_display_info(plant_name)

        return context

    def post(self, request, *args, **kwargs):
        """Handle form submission"""
        self.object = None  # Required for CreateView when calling get_context_data()
        plant_id = self.kwargs['plant_id']
        plant_name = self.get_plant_name()

        combined_form = CombinedPaginationForm(
            data=request.POST,
            plant_id=plant_id,
            plant_name=plant_name
        )

        if combined_form.is_valid():
            try:
                report = combined_form.save()

                # Add success message
                messages.success(
                    request,
                    f'Pagination report for {plant_name} on {report.issue_date} created successfully!'
                )

                return redirect(self.get_success_url())

            except Exception as e:
                messages.error(request, f'Error saving report: {str(e)}')

        else:
            # Add error message with details (extract plain text, no HTML)
            errors = combined_form.get_errors()
            error_msg = 'Please correct the errors below.'

            # Add detailed error information for debugging
            if errors:
                error_details = []
                for section, error_list in errors.items():
                    if error_list:
                        # Extract plain text from error objects (avoid HTML tags)
                        if hasattr(error_list, 'as_text'):
                            # ErrorDict or ErrorList with as_text method
                            error_text = error_list.as_text().replace('* ', '').strip()
                            if error_text:
                                error_details.append(f"{section}: {error_text}")
                        elif isinstance(error_list, dict):
                            # ErrorDict - extract all field errors
                            for field, field_errors in error_list.items():
                                if field_errors:
                                    # Get plain text error messages
                                    if hasattr(field_errors, 'as_text'):
                                        error_text = field_errors.as_text().replace('* ', '').strip()
                                    else:
                                        error_text = ', '.join([str(e) for e in field_errors])
                                    if error_text:
                                        error_details.append(f"{section}.{field}: {error_text}")
                        elif isinstance(error_list, list):
                            # List of errors
                            plain_errors = []
                            for error_item in error_list:
                                if isinstance(error_item, dict):
                                    # Dict of field errors in formset
                                    for field, field_errors in error_item.items():
                                        if field_errors:
                                            if hasattr(field_errors, 'as_text'):
                                                error_text = field_errors.as_text().replace('* ', '').strip()
                                            else:
                                                error_text = ', '.join([str(e) for e in field_errors])
                                            if error_text:
                                                plain_errors.append(f"{field}: {error_text}")
                                elif hasattr(error_item, 'as_text'):
                                    plain_errors.append(error_item.as_text().replace('* ', '').strip())
                                else:
                                    plain_errors.append(str(error_item))

                            if plain_errors:
                                error_details.append(f"{section}: {'; '.join(plain_errors[:2])}")  # Show first 2 from this section

                if error_details:
                    error_msg += f" Details: {'; '.join(error_details[:3])}"  # Show first 3 errors

            messages.error(request, error_msg)

        # Re-render form with errors
        context = self.get_context_data()
        context['combined_form'] = combined_form
        return render(request, self.template_name, context)


class PaginationListView(PlantPermissionMixin, PlantValidationMixin, ListView):
    """
    List all pagination reports for a specific plant with search and filters
    """
    model = PaginationReport
    template_name = 'pagination_dash/pagination_list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        """Filter by plant and apply search/filters"""
        plant_id = self.kwargs['plant_id']
        queryset = PaginationReport.objects.filter(plant_id=plant_id)

        # Optimize queries
        queryset = queryset.prefetch_related('books', 'gnp_info')

        # Add aggregations
        queryset = queryset.annotate(
            book_count=Count('books'),
            total_snp=Sum('books__snp_pages'),
            total_gnp=Sum('books__gnp_pages_count'),
            total_all_pages=Sum('books__total_pages')
        )

        # Search by issue date
        search_date = self.request.GET.get('search_date')
        if search_date:
            queryset = queryset.filter(issue_date=search_date)

        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date:
            queryset = queryset.filter(issue_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(issue_date__lte=end_date)

        # Order by issue date (most recent first)
        queryset = queryset.order_by('-issue_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pass search parameters back to template
        context['search_date'] = self.request.GET.get('search_date', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')

        return context


class PaginationDetailView(PlantPermissionMixin, PlantValidationMixin, DetailView):
    """
    Display complete read-only view of a pagination report
    """
    model = PaginationReport
    template_name = 'pagination_dash/pagination_detail.html'
    context_object_name = 'report'

    def get_queryset(self):
        """Filter by plant_id to ensure security"""
        plant_id = self.kwargs['plant_id']
        return PaginationReport.objects.filter(plant_id=plant_id).prefetch_related('books', 'gnp_info', 'competitors')

    def get_object(self, queryset=None):
        """Get object and validate plant_id matches"""
        obj = super().get_object(queryset)

        # Ensure report belongs to the plant in URL
        if obj.plant_id != self.kwargs['plant_id']:
            raise Http404("Report not found for this plant")

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add calculated totals
        report = self.object
        context['total_snp'] = report.get_total_snp_pages()
        context['total_gnp'] = report.get_total_gnp_pages()
        context['total_pages'] = report.get_total_pages()
        context['total_jackets'] = report.get_total_gnp_jackets()
        context['book_count'] = report.get_book_count()
        context['competitor_count'] = report.get_competitor_count()

        # Get GNP active publications
        if hasattr(report, 'gnp_info'):
            context['active_publications'] = report.gnp_info.get_active_publications()
        else:
            context['active_publications'] = []

        # Add GNP configuration
        plant_name = self.get_plant_name()
        context['has_gnp'] = has_gnp_publications(plant_name)
        context['gnp_publications'] = get_publication_display_info(plant_name)

        return context


class PaginationUpdateView(PlantPermissionMixin, PlantValidationMixin, UpdateView):
    """
    Update existing pagination report
    """
    model = PaginationReport
    template_name = 'pagination_dash/pagination_form.html'
    fields = []  # Required by UpdateView, but we use CombinedPaginationForm instead

    def get_success_url(self):
        """Redirect to detail view after successful update"""
        return reverse('pagination_dash:pagination_detail', kwargs={
            'plant_id': self.kwargs['plant_id'],
            'pk': self.object.pk
        })

    def get_queryset(self):
        """Filter by plant_id"""
        plant_id = self.kwargs['plant_id']
        return PaginationReport.objects.filter(plant_id=plant_id)

    def get_object(self, queryset=None):
        """Get object and validate plant_id matches"""
        obj = super().get_object(queryset)

        # Ensure report belongs to the plant in URL
        if obj.plant_id != self.kwargs['plant_id']:
            raise Http404("Report not found for this plant")

        return obj

    def get_context_data(self, **kwargs):
        """Add combined form to context"""
        context = super().get_context_data(**kwargs)

        plant_id = self.kwargs['plant_id']
        plant_name = self.get_plant_name()

        if self.request.POST:
            context['combined_form'] = CombinedPaginationForm(
                data=self.request.POST,
                instance=self.object,
                plant_id=plant_id,
                plant_name=plant_name
            )
        else:
            context['combined_form'] = CombinedPaginationForm(
                instance=self.object,
                plant_id=plant_id,
                plant_name=plant_name
            )

        context['action'] = 'Update'
        context['submit_text'] = 'Update Report'

        # Add GNP configuration
        context['has_gnp'] = has_gnp_publications(plant_name)
        context['gnp_publications'] = get_publication_display_info(plant_name)

        return context

    def post(self, request, *args, **kwargs):
        """Handle form submission"""
        self.object = self.get_object()
        plant_id = self.kwargs['plant_id']
        plant_name = self.get_plant_name()

        combined_form = CombinedPaginationForm(
            data=request.POST,
            instance=self.object,
            plant_id=plant_id,
            plant_name=plant_name
        )

        if combined_form.is_valid():
            try:
                report = combined_form.save()

                # Add success message
                messages.success(
                    request,
                    f'Pagination report for {plant_name} on {report.issue_date} updated successfully!'
                )

                return redirect(self.get_success_url())

            except Exception as e:
                messages.error(request, f'Error updating report: {str(e)}')

        else:
            # Add error message with details (extract plain text, no HTML)
            errors = combined_form.get_errors()
            error_msg = 'Please correct the errors below.'

            # Add detailed error information for debugging
            if errors:
                error_details = []
                for section, error_list in errors.items():
                    if error_list:
                        # Extract plain text from error objects (avoid HTML tags)
                        if hasattr(error_list, 'as_text'):
                            # ErrorDict or ErrorList with as_text method
                            error_text = error_list.as_text().replace('* ', '').strip()
                            if error_text:
                                error_details.append(f"{section}: {error_text}")
                        elif isinstance(error_list, dict):
                            # ErrorDict - extract all field errors
                            for field, field_errors in error_list.items():
                                if field_errors:
                                    # Get plain text error messages
                                    if hasattr(field_errors, 'as_text'):
                                        error_text = field_errors.as_text().replace('* ', '').strip()
                                    else:
                                        error_text = ', '.join([str(e) for e in field_errors])
                                    if error_text:
                                        error_details.append(f"{section}.{field}: {error_text}")
                        elif isinstance(error_list, list):
                            # List of errors
                            plain_errors = []
                            for error_item in error_list:
                                if isinstance(error_item, dict):
                                    # Dict of field errors in formset
                                    for field, field_errors in error_item.items():
                                        if field_errors:
                                            if hasattr(field_errors, 'as_text'):
                                                error_text = field_errors.as_text().replace('* ', '').strip()
                                            else:
                                                error_text = ', '.join([str(e) for e in field_errors])
                                            if error_text:
                                                plain_errors.append(f"{field}: {error_text}")
                                elif hasattr(error_item, 'as_text'):
                                    plain_errors.append(error_item.as_text().replace('* ', '').strip())
                                else:
                                    plain_errors.append(str(error_item))

                            if plain_errors:
                                error_details.append(f"{section}: {'; '.join(plain_errors[:2])}")  # Show first 2 from this section

                if error_details:
                    error_msg += f" Details: {'; '.join(error_details[:3])}"  # Show first 3 errors

            messages.error(request, error_msg)

        # Re-render form with errors
        context = self.get_context_data()
        context['combined_form'] = combined_form
        return render(request, self.template_name, context)


class PaginationDeleteView(PlantValidationMixin, DeleteView):
    """
    Delete pagination report with confirmation
    """
    model = PaginationReport
    template_name = 'pagination_dash/pagination_confirm_delete.html'
    context_object_name = 'report'

    def get_success_url(self):
        """Redirect to list view after deletion"""
        return reverse_lazy('pagination_dash:pagination_list', kwargs={'plant_id': self.kwargs['plant_id']})

    def get_queryset(self):
        """Filter by plant_id"""
        plant_id = self.kwargs['plant_id']
        return PaginationReport.objects.filter(plant_id=plant_id)

    def get_object(self, queryset=None):
        """Get object and validate plant_id matches"""
        obj = super().get_object(queryset)

        # Ensure report belongs to the plant in URL
        if obj.plant_id != self.kwargs['plant_id']:
            raise Http404("Report not found for this plant")

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add calculated totals for display
        report = self.object
        context['total_pages'] = report.get_total_pages()
        context['book_count'] = report.get_book_count()

        return context

    def delete(self, request, *args, **kwargs):
        """Handle deletion with success message"""
        self.object = self.get_object()
        plant_name = self.get_plant_name()
        issue_date = self.object.issue_date

        # Delete the report
        self.object.delete()

        # Add success message
        messages.success(
            request,
            f'Pagination report for {plant_name} on {issue_date} deleted successfully!'
        )

        return redirect(self.get_success_url())
