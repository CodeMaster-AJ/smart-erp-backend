from django.db import models


class Production(models.Model):
    product = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    qty = models.PositiveIntegerField()
    date = models.DateField()
    status = models.CharField(max_length=20, default='Completed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.qty}"


class Inventory(models.Model):
    product = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default='Raw Material')
    stock = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default='pcs')
    last_in = models.PositiveIntegerField(default=0)
    last_out = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product


class StockHistory(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='history')
    type = models.CharField(max_length=3)
    quantity = models.PositiveIntegerField()
    balance = models.PositiveIntegerField()
    note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} {self.quantity} of {self.inventory.product}"


class Training(models.Model):
    title = models.CharField(max_length=200)
    trainer = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    seats = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default='Open')
    location = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def enrolled_count(self):
        return self.trainees.count()


class Trainee(models.Model):
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='trainees')
    name = models.CharField(max_length=100)
    village = models.CharField(max_length=100, default='')
    enroll_date = models.DateField(auto_now_add=True)
    completion = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default='Enrolled')
    note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
