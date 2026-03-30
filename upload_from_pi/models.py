from django.db import models

# Create your models here.
class ProductionReport(models.Model):
    FOLDER_COUNT_CHOICES = [
        (1, '1'),
        (2, '2'),
    ]

    issueid = models.CharField(max_length=30, primary_key=True)
    issue_date = models.DateField(db_index=True)
    runid = models.CharField(max_length=20)
    edition = models.CharField(max_length=100)
    products = models.CharField(max_length=200, db_index=True)
    main_supplement = models.CharField(max_length=20)
    no_of_books = models.IntegerField()
    machine = models.CharField(max_length=20)
    folder = models.CharField(max_length=20, db_index=True)
    print_order = models.IntegerField()
    gross_counter = models.IntegerField()
    waste = models.IntegerField()
    waste_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    production_start = models.DateTimeField()
    production_end = models.DateTimeField()
    production_start_date = models.DateField()
    production_end_date = models.DateField()
    total_run_time_mnts = models.IntegerField()
    total_downtime = models.IntegerField()
    number_of_stoppages = models.IntegerField()
    wb_s = models.IntegerField()
    avg_speed = models.DecimalField(max_digits=10, decimal_places=2)
    total_pages = models.CharField(max_length=30)
    sum_of_pages = models.IntegerField()
    color_pages = models.CharField(max_length=30, null=True)
    bw_pages = models.CharField(max_length=20, null=True)
    broad_sheets = models.CharField(max_length=50, null=True)
    tabloid = models.CharField(max_length=30, null=True)
    user_name = models.CharField(max_length=100, null=True)
    in_charge = models.CharField(max_length=100, null=True)
    machine_in_charge = models.CharField(max_length=100, null=True)
    officers = models.TextField(null=True)
    remarks = models.TextField(null=True)
    accidents = models.TextField(null=True)
    print_finish_delay_reason = models.TextField(null=True)
    entry_time = models.DateTimeField()
    plant_name = models.CharField(max_length=50)
    complexity = models.CharField(max_length=3)
    complexities = models.CharField(max_length=10)
    production_type = models.CharField(max_length=20)
    reason_for_additional_folder = models.CharField(max_length=50, null=True)
    uv = models.CharField(max_length=3)
    last_truck = models.CharField(max_length=10, null=True)
    last_bundle = models.CharField(max_length=10, null=True)
    towers_used = models.CharField(max_length=100, null=True)
    towers_count = models.IntegerField(null=True)
    run_date = models.DateField()
    status = models.CharField(max_length=1, null=True)
    folders_count = models.IntegerField(choices=FOLDER_COUNT_CHOICES)
    uv_run = models.BooleanField()
    toi_city = models.BooleanField(default=False)
    final_score = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    innovation_rank = models.CharField(max_length=5, null=True)
    predicted_runtime = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    runtime_score = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    runtime_variance = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    waste_score = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    waste_variance = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = 'production_report'
        indexes = [
            models.Index(fields=['issue_date']),
            models.Index(fields=['folder']),
            models.Index(fields=['products']),
            models.Index(fields=['folders_count']),
            models.Index(fields=['uv_run']),
        ]

    def __str__(self):
        return f"Production Report {self.issueid}"


class Innovation(models.Model):
    innovation_id = models.CharField(max_length=100, primary_key=True)
    issueid = models.ForeignKey(
        ProductionReport,
        on_delete=models.CASCADE,
        related_name='innovations'
    )
    bookid = models.CharField(max_length=24)
    issue_date = models.DateField()
    runid = models.IntegerField(null=True)
    product_name = models.CharField(max_length=200)
    desk = models.CharField(max_length=100)
    edition = models.CharField(max_length=100)
    machine = models.CharField(max_length=50)
    folder = models.CharField(max_length=50)
    innovation = models.CharField(max_length=100)
    impact = models.DecimalField(max_digits=10, decimal_places=2)
    complexity = models.BooleanField(null=True)
    complexities = models.CharField(max_length=100, null=True)
    plant_name = models.CharField(max_length=100)
    production_type = models.CharField(max_length=5, null=True)
    uv = models.BooleanField(default=False, null=True)
    reflong = models.BooleanField(default=False, null=True)

    class Meta:
        db_table = 'innovations'
        indexes = [
            models.Index(fields=['bookid']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['runid'])
        ]

    def __str__(self):
        return f"{self.product_name} - {self.issue_date} - {self.innovation}"


class BookWiseDetails(models.Model):
    issueid = models.ForeignKey(ProductionReport, on_delete=models.CASCADE, related_name='book_wise_details', to_field='issueid')
    book_id = models.CharField(max_length=50, unique=True, primary_key=True)
    issue_date = models.DateField()
    runid = models.CharField(max_length=50, null=True)
    product_name = models.CharField(max_length=200)
    edition = models.CharField(max_length=100)
    sub_product = models.CharField(max_length=100, null=True, blank=True)
    main_supplement = models.CharField(max_length=50)
    machine = models.CharField(max_length=50)
    folder = models.CharField(max_length=50)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    print_order = models.IntegerField()
    gross_counter = models.IntegerField()
    color_pages = models.IntegerField()
    bw_pages = models.IntegerField()
    product_type = models.CharField(max_length=50)
    total_pages = models.IntegerField()
    waste = models.IntegerField()
    waste_percentage = models.DecimalField(max_digits=7, decimal_places=2)
    ctp_product = models.CharField(max_length=200, null=True)
    editorial_release = models.DateTimeField(null=True)
    first_tiff = models.DateTimeField(null=True)
    last_tiff = models.DateTimeField(null=True)
    last_plate = models.DateTimeField(null=True)
    plate_issued = models.IntegerField(null=True)
    replates = models.IntegerField(null=True)
    book_type = models.CharField(max_length=50, null=True)
    startup_waste = models.IntegerField(null=True)
    baloon_folder = models.IntegerField(null=True)
    total_run_time_mnts = models.IntegerField(null=True)
    total_downtime = models.IntegerField(null=True)
    no_of_stoppages = models.IntegerField(null=True)
    w_bs = models.IntegerField(null=True)
    production_type = models.CharField(max_length=50, null=True)
    avg_speed = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    change_over_time_mins = models.IntegerField(null=True)
    change_over_type = models.CharField(max_length=100, null=True)
    user = models.CharField(max_length=100)
    entry_time = models.DateTimeField()
    plant_name = models.CharField(max_length=100)
    complexity = models.CharField(max_length=50)
    complexities = models.CharField(max_length=100)
    desk = models.CharField(max_length=100)
    reflong = models.CharField(max_length=10, null=True)
    reason_for_additional_folder = models.TextField(null=True, blank=True)
    uv = models.CharField(max_length=10)
    last_truck = models.CharField(max_length=20, null=True, blank=True)
    run_date = models.DateField()
    sap_code = models.CharField(max_length=50)
    integrated_pullout = models.CharField(max_length=50, null=True, blank=True)
    gnp_pages = models.CharField(max_length=50, null=True, blank=True)
    last_bundle = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'book_wise_details'
        indexes = [
            models.Index(fields=['issue_date', 'runid']),
        ]

    def __str__(self):
        return f"{self.product_name} - {self.issue_date}"


class Downtime(models.Model):
    downtime_id = models.CharField(max_length=100, primary_key=True)
    issueid = models.ForeignKey(ProductionReport, on_delete=models.CASCADE, related_name='downtimes', to_field='issueid')
    edition_date = models.DateField()
    runid = models.CharField(max_length=50, null=True)
    edition = models.CharField(max_length=200)
    main_supplement = models.CharField(max_length=50)
    gnp_snp = models.CharField(max_length=50)
    machine = models.CharField(max_length=50)
    folder = models.CharField(max_length=50)
    department = models.CharField(max_length=100, null=True)
    related = models.CharField(max_length=100, null=True)
    reason = models.TextField(null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_downtime = models.IntegerField()
    complexity = models.CharField(max_length=10, null=True)
    complexities = models.TextField(null=True)
    cutoff_waste = models.IntegerField()
    scum_waste = models.IntegerField()
    white_waste = models.IntegerField()
    other = models.IntegerField()
    scheduled = models.CharField(max_length=10, null=True)
    follow_up_date = models.DateField(null=True, blank=True)
    action_taken = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    plant_name = models.CharField(max_length=100)
    production_type = models.CharField(max_length=10)
    uv = models.CharField(max_length=10)
    run_date = models.DateField()

    class Meta:
        db_table = 'downtime'
        indexes = [
            models.Index(fields=['edition_date', 'runid']),
        ]

    def __str__(self):
        return f"Downtime for {self.issueid} on {self.edition_date}"


class WebBreak(models.Model):
    web_break_id = models.CharField(max_length=100, primary_key=True)
    issueid = models.ForeignKey(ProductionReport, on_delete=models.CASCADE, related_name='web_breaks', to_field='issueid')
    edition_date = models.DateField()
    runid = models.CharField(max_length=50, null=True)
    edition = models.CharField(max_length=200)
    machine = models.CharField(max_length=50)
    folder = models.CharField(max_length=50)
    sapid = models.CharField(max_length=50)
    reelstand = models.CharField(max_length=50, null=True)
    arm = models.CharField(max_length=50, null=True)
    material_code = models.CharField(max_length=100, null=True)
    material = models.CharField(max_length=200, null=True)
    manufacturer = models.CharField(max_length=100, null=True)
    gsm = models.IntegerField(null=True)
    color = models.CharField(max_length=10, null=True)
    paper_type = models.CharField(max_length=50, null=True)
    operator = models.CharField(max_length=100, null=True)
    reason = models.TextField(null=True)
    plant_name = models.CharField(max_length=100)
    products = models.CharField(max_length=200, null=True)
    main_supplement = models.CharField(max_length=50, null=True)
    no_of_books = models.IntegerField(null=True)
    complexity = models.CharField(max_length=10, null=True)
    complexities = models.TextField(null=True)
    production_type = models.CharField(max_length=10, null=True)
    uv = models.CharField(max_length=10)
    run_date = models.DateField()
    manufacture_code = models.CharField(max_length=100, null=True, blank=True)
    defect_code = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'web_break'
        indexes = [
            models.Index(fields=['edition_date', 'runid']),
        ]

    def __str__(self):
        return f"Web Break for {self.issueid} on {self.edition_date}"


class ReelConsumption(models.Model):
    reel_consumption_id = models.CharField(max_length=100, primary_key=True)
    issueid = models.ForeignKey(ProductionReport, on_delete=models.CASCADE, related_name='reel_consumptions', to_field='issueid')
    edition_date = models.DateField()
    runid = models.CharField(max_length=50, null=True)
    edition = models.CharField(max_length=200)
    sapid = models.CharField(max_length=50)
    captured_consumption = models.IntegerField()
    actual_consumption = models.IntegerField()
    sap_weight = models.IntegerField()
    machine = models.CharField(max_length=50, null=True)
    reelstand = models.CharField(max_length=50, null=True)
    material_code = models.CharField(max_length=100, null=True)
    material = models.CharField(max_length=200, null=True)
    manufacturer = models.CharField(max_length=100, null=True)
    gsm = models.IntegerField(null=True)
    color = models.CharField(max_length=10, null=True)
    paper_type = models.CharField(max_length=50, null=True)
    no_of_wb = models.IntegerField(null=True)
    operator = models.CharField(max_length=100, null=True)
    plant = models.CharField(max_length=100, null=True)
    production_type_folder = models.CharField(max_length=10, null=True) # Renamed from production_type to avoid conflict
    folder = models.CharField(max_length=50, null=True)
    manufacture_code = models.CharField(max_length=100, null=True, blank=True)
    defect_code = models.CharField(max_length=100, null=True, blank=True)
    product_name = models.TextField(null=True)
    np_size_code = models.CharField(max_length=10, null=True)
    np_width_in_pgs = models.IntegerField(null=True)
    print_order = models.IntegerField(null=True)
    production_type_factor = models.IntegerField(null=True)

    class Meta:
        db_table = 'reel_consumption'
        indexes = [
            models.Index(fields=['edition_date', 'runid']),
        ]

    def __str__(self):
        return f"Reel Consumption for {self.issueid} on {self.edition_date}"
