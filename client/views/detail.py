from django.shortcuts               import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http                    import JsonResponse
from authentication.decorators      import client_required
from supervisor.models.data         import Data
from supervisor.models.project      import Project
from supervisor.models.node         import Node
from camera_management.models      import Camera, Detection
from django.utils                   import timezone
import datetime
#lezim ya3mil login
@login_required(login_url='client_login')
#lezim ykoun client mich admin 
@client_required
#yit2akid mil projet mawjoud o teba3 client
def node_detail(request, project_id, node_id):
    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
#capteur teba3 machrou3
    node = get_object_or_404(Node, id=node_id, parcelle__project=project)

    #* Filtrer les données pour les dernières 24 heures
    now = timezone.now()
    start_of_period = now - datetime.timedelta(days=1)

    data_entries = Data.objects.filter(node=node, published_date__range=(start_of_period, now))

    # Fallback to the last 24 hours relative to the most recent data point if no recent data exists
    if not data_entries.exists():
        last_entry = Data.objects.filter(node=node).order_by('-published_date').first()
        if last_entry:
            now = last_entry.published_date
            start_of_period = now - datetime.timedelta(days=1)
            data_entries = Data.objects.filter(node=node, published_date__range=(start_of_period, now))


    temperatures = [{'interval': entry.published_date.isoformat(), 'temperature': entry.temperature} for entry in data_entries if entry.temperature is not None]
    humidity = [{'interval': entry.published_date.isoformat(), 'humidity': entry.humidity} for entry in data_entries if entry.humidity is not None]
    gas = [{'interval': entry.published_date.isoformat(), 'gas': entry.gaz} for entry in data_entries if entry.gaz is not None]
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'temperatures': temperatures,
            'humidity': humidity,
            'gas': gas
        })

    context = {
        'project': project,
        'node': node,
        'temperatures': temperatures,
        'humidity': humidity,
        'gas': gas,
    }

    return render(request, 'website/node_detail.html', context)


