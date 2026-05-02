import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from accounts.models import Token
from operations.models import Village, Unit
from main.models import Production, Inventory, StockHistory, Training, Trainee


class Command(BaseCommand):
    help = 'Create demo users and seed all sample data'

    def handle(self, *args, **options):
        self.stdout.write('─── Creating demo users ───')

        users_data = [
            ('admin@erp.in',   'Admin',   'User',   'SmartErp@2026!', 'admin'),
            ('manager@erp.in', 'Priya',   'Sharma', 'SmartErp@2026!', 'manager'),
            ('staff@erp.in',   'Ravi',    'Kumar',  'SmartErp@2026!', 'staff'),
        ]

        for email, first, last, password, role in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email, 'first_name': first, 'last_name': last}
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'  Created user: {email}')

            group, _ = Group.objects.get_or_create(name=role.capitalize())
            user.groups.set([group])

            token, created = Token.objects.get_or_create(user=user)
            if created or not token.key:
                token.key = secrets.token_urlsafe(32)
                token.save()

        self.stdout.write('─── Seeding Villages ───')

        villages_data = [
            ('Rampur',   'Amethi',     1240, 'Active'),
            ('Devpur',   'Sultanpur',   980, 'Active'),
            ('Nawalpur', 'Barabanki',   640, 'Inactive'),
            ('Sitapur',  'Raebareli',  2100, 'Active'),
        ]
        villages = {}
        for name, district, pop, status in villages_data:
            v, _ = Village.objects.get_or_create(name=name, defaults={
                'district': district, 'population': pop, 'status': status
            })
            villages[name] = v
            self.stdout.write(f'  Village: {v.name}')

        self.stdout.write('─── Seeding Units ───')

        units_data = [
            ('Rampur',   'Weaving Unit A',    'Textile',    50, 18),
            ('Rampur',   'Pottery Workshop',  'Ceramics',   20, 8),
            ('Devpur',   'Bamboo Craft',      'Handicraft', 30, 12),
            ('Sitapur',  'Pickle Processing', 'Food',       40, 22),
        ]
        units = {}
        for village_name, name, utype, capacity, workers in units_data:
            u, _ = Unit.objects.get_or_create(name=name, defaults={
                'village': villages[village_name],
                'type': utype, 'capacity': capacity, 'workers': workers
            })
            units[name] = u
            self.stdout.write(f'  Unit: {u.name} ({village_name})')

        self.stdout.write('─── Seeding Production ───')

        prod_data = [
            ('Cotton Fabric', 'Weaving Unit A',    120, '2025-03-10', 'Completed'),
            ('Clay Pots',     'Pottery Workshop',   85, '2025-03-11', 'Completed'),
            ('Bamboo Basket', 'Bamboo Craft',       60, '2025-03-12', 'In Progress'),
            ('Mango Pickle',  'Pickle Processing', 200, '2025-03-13', 'Completed'),
            ('Cotton Fabric', 'Weaving Unit A',    145, '2025-03-14', 'Completed'),
        ]
        for product, unit, qty, date, status in prod_data:
            Production.objects.get_or_create(
                product=product, unit=unit, date=date,
                defaults={'qty': qty, 'status': status}
            )
            self.stdout.write(f'  Production: {product} x{qty}')

        self.stdout.write('─── Seeding Inventory ───')

        inv_data = [
            ('Cotton Thread', 'Raw Material',   430, 100, 'kg'),
            ('Clay',          'Raw Material',   180, 200, 'kg'),
            ('Bamboo',        'Raw Material',    95, 150, 'pcs'),
            ('Glass Jars',    'Packaging',      620, 100, 'pcs'),
            ('Cotton Fabric', 'Finished Goods', 265,  50, 'meters'),
            ('Bamboo Basket', 'Finished Goods',  60,  40, 'pcs'),
        ]
        for product, category, stock, min_stock, unit in inv_data:
            inv, _ = Inventory.objects.get_or_create(product=product, defaults={
                'category': category, 'stock': stock,
                'min_stock': min_stock, 'unit': unit
            })
            self.stdout.write(f'  Inventory: {product} ({stock} {unit})')

        self.stdout.write('─── Seeding Trainings ───')

        trainings_data = [
            ('Natural Dyeing Techniques',   'Dr. Kavita Singh',   '2025-03-15', '2025-03-20', 20, 'Ongoing', 'Rampur Community Hall'),
            ('Basic Accounting & Records',  'Mr. Ramesh Gupta',   '2025-03-22', '2025-03-24', 15, 'Full',    'Devpur Training Center'),
            ('Quality Control in Handloom', 'Mrs. Sunita Devi',   '2025-04-01', '2025-04-05', 25, 'Open',    'Sitapur Unit Hall'),
            ('Digital Marketing for Crafts','Ms. Priya Sharma',   '2025-04-10', '2025-04-12', 20, 'Open',    'Online / Zoom'),
        ]
        training_objs = {}
        for title, trainer, start, end, seats, status, location in trainings_data:
            t, _ = Training.objects.get_or_create(title=title, defaults={
                'trainer': trainer, 'start_date': start, 'end_date': end,
                'seats': seats, 'status': status, 'location': location
            })
            training_objs[title] = t
            self.stdout.write(f'  Training: {t.title}')

        self.stdout.write('─── Seeding Trainees ───')

        trainees_data = [
            ('Rekha Devi',   'Natural Dyeing Techniques',   'Rampur',   60, 'Active'),
            ('Sundar Lal',   'Natural Dyeing Techniques',   'Devpur',   60, 'Active'),
            ('Meena Kumari', 'Basic Accounting & Records',  'Sitapur', 100, 'Completed'),
            ('Asha Devi',    'Quality Control in Handloom', 'Nawalpur',  0, 'Enrolled'),
            ('Vijay Kumar',  'Digital Marketing for Crafts','Rampur',    0, 'Enrolled'),
        ]
        for name, training_title, village, completion, status in trainees_data:
            t = training_objs[training_title]
            Trainee.objects.get_or_create(
                name=name, training=t,
                defaults={'village': village, 'completion': completion, 'status': status}
            )
            self.stdout.write(f'  Trainee: {name}')

        self.stdout.write(self.style.SUCCESS('─── All data seeded! ───'))
