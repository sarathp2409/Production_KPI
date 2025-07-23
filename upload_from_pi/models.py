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
    user_name = models.CharField(max_length=50, null=True)
    in_charge = models.CharField(max_length=50, null=True)
    machine_in_charge = models.CharField(max_length=50, null=True)
    officers = models.CharField(max_length=100, null=True)
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
