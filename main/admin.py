from django.contrib import admin
from .models import Production, Inventory, StockHistory, Training, Trainee

admin.site.register(Production)
admin.site.register(Inventory)
admin.site.register(StockHistory)
admin.site.register(Training)
admin.site.register(Trainee)
