import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Village, Unit


def serialize_village(v):
    return {
        'id': v.id,
        'name': v.name,
        'district': v.district,
        'population': v.population,
        'units': v.unit_count,
        'status': v.status,
    }


def serialize_unit(u):
    return {
        'id': u.id,
        'name': u.name,
        'village_id': u.village_id,
        'villageId': u.village_id,
        'villageName': u.village.name,
        'type': u.type,
        'capacity': u.capacity or 0,
        'workers': u.workers or 0,
    }


# ── Villages ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def village_list(request):
    if request.method == 'GET':
        villages = Village.objects.all().order_by('id')
        return JsonResponse([serialize_village(v) for v in villages], safe=False)

    data = json.loads(request.body)
    village = Village.objects.create(
        name=data.get('name', ''),
        district=data.get('district', ''),
        population=int(data.get('population', 0)),
        status=data.get('status', 'Active'),
    )
    return JsonResponse(serialize_village(village), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def village_detail(request, pk):
    try:
        village = Village.objects.get(pk=pk)
    except Village.DoesNotExist:
        return JsonResponse({'message': 'Village not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse(serialize_village(village))

    if request.method == 'DELETE':
        village.delete()
        return JsonResponse({'message': 'Deleted'})

    data = json.loads(request.body)
    village.name = data.get('name', village.name)
    village.district = data.get('district', village.district)
    village.population = int(data.get('population', village.population))
    village.status = data.get('status', village.status)
    village.save()
    return JsonResponse(serialize_village(village))


@csrf_exempt
@require_http_methods(["GET"])
def village_units(request, pk):
    try:
        village = Village.objects.get(pk=pk)
    except Village.DoesNotExist:
        return JsonResponse({'message': 'Village not found'}, status=404)

    units = village.units.all().order_by('id')
    return JsonResponse([serialize_unit(u) for u in units], safe=False)


# ── Units ────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def unit_list(request):
    if request.method == 'GET':
        units = Unit.objects.select_related('village').all().order_by('id')
        return JsonResponse([serialize_unit(u) for u in units], safe=False)

    data = json.loads(request.body)
    village_id = data.get('village_id') or data.get('villageId')
    try:
        village = Village.objects.get(pk=village_id)
    except Village.DoesNotExist:
        return JsonResponse({'message': 'Village not found'}, status=400)

    unit = Unit.objects.create(
        village=village,
        name=data.get('name', ''),
        type=data.get('type', 'Textile'),
        capacity=int(data['capacity']) if data.get('capacity') else None,
        workers=int(data['workers']) if data.get('workers') else None,
    )
    return JsonResponse(serialize_unit(unit), status=201)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def unit_detail(request, pk):
    try:
        unit = Unit.objects.select_related('village').get(pk=pk)
    except Unit.DoesNotExist:
        return JsonResponse({'message': 'Unit not found'}, status=404)

    if request.method == 'DELETE':
        unit.delete()
        return JsonResponse({'message': 'Deleted'})

    data = json.loads(request.body)
    unit.name = data.get('name', unit.name)
    unit.type = data.get('type', unit.type)

    if data.get('village_id') or data.get('villageId'):
        vid = data.get('village_id') or data.get('villageId')
        unit.village = Village.objects.get(pk=vid)

    if data.get('capacity') is not None:
        unit.capacity = int(data['capacity']) or None
    if data.get('workers') is not None:
        unit.workers = int(data['workers']) or None

    unit.save()
    return JsonResponse(serialize_unit(unit))
