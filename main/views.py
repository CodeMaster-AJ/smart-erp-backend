import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from .models import Production, Inventory, StockHistory, Training, Trainee


# ── Serializers ────────────────────────────────────────────────────────

def serialize_production(p):
    return {
        'id': p.id,
        'product': p.product,
        'unit': p.unit,
        'qty': p.qty,
        'date': str(p.date),
        'status': p.status,
    }


def serialize_inventory(inv):
    return {
        'id': inv.id,
        'product': inv.product,
        'category': inv.category,
        'stock': inv.stock,
        'minStock': inv.min_stock,
        'unit': inv.unit,
        'lastIn': inv.last_in,
        'lastOut': inv.last_out,
    }


def serialize_history(h):
    return {
        'id': h.id,
        'date': str(h.created_at.date()),
        'type': h.type,
        'qty': h.quantity,
        'balance': h.balance,
        'note': h.note,
    }


def serialize_training(t):
    return {
        'id': t.id,
        'title': t.title,
        'trainer': t.trainer,
        'startDate': str(t.start_date),
        'endDate': str(t.end_date),
        'seats': t.seats,
        'enrolled': t.enrolled_count,
        'status': t.status,
        'location': t.location,
    }


def serialize_trainee(t):
    return {
        'id': t.id,
        'name': t.name,
        'training_id': t.training_id,
        'trainingTitle': t.training.title,
        'village': t.village,
        'enrollDate': str(t.enroll_date),
        'completion': t.completion,
        'status': t.status,
    }


# ── Production ─────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def production_list(request):
    if request.method == 'GET':
        qs = Production.objects.all().order_by('-id')
        status_filter = request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return JsonResponse([serialize_production(p) for p in qs], safe=False)

    data = json.loads(request.body)
    p = Production.objects.create(
        product=data.get('product', ''),
        unit=data.get('unit', ''),
        qty=int(data.get('qty', 0)),
        date=data.get('date', ''),
        status=data.get('status', 'Completed'),
    )
    return JsonResponse(serialize_production(p), status=201)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def production_detail(request, pk):
    try:
        p = Production.objects.get(pk=pk)
    except Production.DoesNotExist:
        return JsonResponse({'message': 'Not found'}, status=404)

    if request.method == 'DELETE':
        p.delete()
        return JsonResponse({'message': 'Deleted'})

    data = json.loads(request.body)
    p.product = data.get('product', p.product)
    p.unit = data.get('unit', p.unit)
    p.qty = int(data.get('qty', p.qty))
    p.date = data.get('date', p.date)
    p.status = data.get('status', p.status)
    p.save()
    return JsonResponse(serialize_production(p))


# ── Inventory ──────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def inventory_list(request):
    if request.method == 'GET':
        items = Inventory.objects.all().order_by('id')
        return JsonResponse([serialize_inventory(i) for i in items], safe=False)

    data = json.loads(request.body)
    item = Inventory.objects.create(
        product=data.get('product', ''),
        category=data.get('category', 'Raw Material'),
        stock=int(data.get('stock', 0)),
        min_stock=int(data.get('min_stock', 0)),
        unit=data.get('unit', 'pcs'),
    )
    return JsonResponse(serialize_inventory(item), status=201)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def inventory_detail(request, pk):
    try:
        item = Inventory.objects.get(pk=pk)
    except Inventory.DoesNotExist:
        return JsonResponse({'message': 'Not found'}, status=404)

    if request.method == 'DELETE':
        item.delete()
        return JsonResponse({'message': 'Deleted'})

    data = json.loads(request.body)
    item.product = data.get('product', item.product)
    item.category = data.get('category', item.category)
    item.unit = data.get('unit', item.unit)
    if 'min_stock' in data:
        item.min_stock = int(data['min_stock'])
    if data.get('stock') is not None:
        item.stock = int(data['stock'])
    item.save()
    return JsonResponse(serialize_inventory(item))


# ── Stock In / Out ─────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def stock_in(request):
    data = json.loads(request.body)
    inv_id = data.get('inventory_id')
    qty = int(data.get('quantity', 0))
    note = data.get('note', '')

    if not inv_id or qty <= 0:
        return JsonResponse({'message': 'Invalid data'}, status=400)

    try:
        item = Inventory.objects.get(pk=inv_id)
    except Inventory.DoesNotExist:
        return JsonResponse({'message': 'Inventory item not found'}, status=404)

    item.stock += qty
    item.last_in = qty
    item.save()

    StockHistory.objects.create(
        inventory=item,
        type='in',
        quantity=qty,
        balance=item.stock,
        note=note,
    )
    return JsonResponse({'message': 'Stock added', 'item': serialize_inventory(item)})


@csrf_exempt
@require_http_methods(["POST"])
def stock_out(request):
    data = json.loads(request.body)
    inv_id = data.get('inventory_id')
    qty = int(data.get('quantity', 0))
    note = data.get('note', '')

    if not inv_id or qty <= 0:
        return JsonResponse({'message': 'Invalid data'}, status=400)

    try:
        item = Inventory.objects.get(pk=inv_id)
    except Inventory.DoesNotExist:
        return JsonResponse({'message': 'Inventory item not found'}, status=404)

    if qty > item.stock:
        return JsonResponse({'message': 'Insufficient stock'}, status=400)

    item.stock -= qty
    item.last_out = qty
    item.save()

    StockHistory.objects.create(
        inventory=item,
        type='out',
        quantity=qty,
        balance=item.stock,
        note=note,
    )
    return JsonResponse({'message': 'Stock removed', 'item': serialize_inventory(item)})


@csrf_exempt
@require_http_methods(["GET"])
def stock_history(request, pk):
    try:
        item = Inventory.objects.get(pk=pk)
    except Inventory.DoesNotExist:
        return JsonResponse({'message': 'Not found'}, status=404)

    history = item.history.all().order_by('-created_at')
    return JsonResponse([serialize_history(h) for h in history], safe=False)


# ── Training ───────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def training_list(request):
    if request.method == 'GET':
        trainings = Training.objects.annotate(
            enrolled_count=Count('trainees')
        ).order_by('id')
        return JsonResponse([serialize_training(t) for t in trainings], safe=False)

    data = json.loads(request.body)
    t = Training.objects.create(
        title=data.get('title', ''),
        trainer=data.get('trainer', ''),
        start_date=data.get('startDate', ''),
        end_date=data.get('endDate', ''),
        seats=int(data.get('seats', 0)),
        status=data.get('status', 'Open'),
        location=data.get('location', ''),
    )
    return JsonResponse(serialize_training(t), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def training_detail(request, pk):
    try:
        t = Training.objects.get(pk=pk)
    except Training.DoesNotExist:
        return JsonResponse({'message': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse(serialize_training(t))

    if request.method == 'DELETE':
        t.delete()
        return JsonResponse({'message': 'Deleted'})

    data = json.loads(request.body)
    t.title = data.get('title', t.title)
    t.trainer = data.get('trainer', t.trainer)
    t.start_date = data.get('startDate', t.start_date)
    t.end_date = data.get('endDate', t.end_date)
    t.seats = int(data.get('seats', t.seats))
    t.status = data.get('status', t.status)
    t.location = data.get('location', t.location)
    t.save()
    return JsonResponse(serialize_training(t))


# ── Trainees ───────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def trainee_list(request):
    if request.method == 'GET':
        trainees = Trainee.objects.select_related('training').all().order_by('id')
        return JsonResponse([serialize_trainee(t) for t in trainees], safe=False)

    data = json.loads(request.body)
    training_id = data.get('training_id')
    try:
        training = Training.objects.get(pk=training_id)
    except Training.DoesNotExist:
        return JsonResponse({'message': 'Training not found'}, status=404)

    trainee = Trainee.objects.create(
        training=training,
        name=data.get('name', ''),
        village=data.get('village', ''),
        note=data.get('note', ''),
    )
    return JsonResponse(serialize_trainee(trainee), status=201)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def trainee_detail(request, pk):
    try:
        trainee = Trainee.objects.select_related('training').get(pk=pk)
    except Trainee.DoesNotExist:
        return JsonResponse({'message': 'Not found'}, status=404)

    if request.method == 'DELETE':
        trainee.delete()
        return JsonResponse({'message': 'Deleted'})

    data = json.loads(request.body)
    trainee.name = data.get('name', trainee.name)
    trainee.village = data.get('village', trainee.village)

    if 'completion' in data:
        trainee.completion = int(data['completion'])
        c = trainee.completion
        if c == 100:
            trainee.status = 'Completed'
        elif c > 0:
            trainee.status = 'Active'
        else:
            trainee.status = 'Enrolled'

    if 'status' in data:
        trainee.status = data['status']

    trainee.save()
    return JsonResponse(serialize_trainee(trainee))


# ── Enroll (create trainee via training endpoint) ──────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def enroll_trainee(request):
    data = json.loads(request.body)
    training_id = data.get('training_id')
    try:
        training = Training.objects.get(pk=training_id)
    except Training.DoesNotExist:
        return JsonResponse({'message': 'Training not found'}, status=404)

    if training.enrolled_count >= training.seats:
        return JsonResponse({'message': 'No seats available'}, status=400)

    trainee = Trainee.objects.create(
        training=training,
        name=data.get('name', ''),
        village=data.get('village', ''),
        note=data.get('note', ''),
    )
    return JsonResponse(serialize_trainee(trainee), status=201)


# ── Dashboard ──────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_summary(request):
    from operations.models import Village, Unit
    return JsonResponse({
        'villages': Village.objects.count(),
        'production': Production.objects.count(),
        'inventory': Inventory.objects.count(),
        'trainings': Training.objects.count(),
    })


@csrf_exempt
@require_http_methods(["GET"])
def dashboard_charts(request):
    return JsonResponse({})
