import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
django.setup()

from supervisor.models.node import Node
from supervisor.models.data import Data

nodes = Node.objects.all()
print(f"Total nodes: {nodes.count()}")
for n in nodes:
    data_count = Data.objects.filter(node=n).count()
    last_data = Data.objects.filter(node=n).order_by('-published_date').first()
    print(f"  Node: {n.name}, Reference: '{n.reference}', Parcelle: {n.parcelle}, Data count: {data_count}")
    if last_data:
        print(f"    Last data: temp={last_data.temperature}, hum={last_data.humidity}, date={last_data.published_date}")
    else:
        print(f"    No data received yet")
