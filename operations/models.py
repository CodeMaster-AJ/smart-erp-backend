from django.db import models


class Village(models.Model):
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    population = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def unit_count(self):
        return self.units.count()


class Unit(models.Model):
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, default='Textile')
    capacity = models.PositiveIntegerField(null=True, blank=True)
    workers = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
