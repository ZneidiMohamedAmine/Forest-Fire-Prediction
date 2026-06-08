import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
django.setup()

from supervisor.models.node import Node
from supervisor.models.project import Project
from django.test import RequestFactory
from client.views.detail import node_detail
from django.contrib.auth.models import User

node = Node.objects.filter(reference='chottmariemnode03').first()
if node:
    project = node.parcelle.project
    print(f"Node ID: {node.id}, Project ID: {project.polygon_id}")
    
    # Simulate an AJAX request
    factory = RequestFactory()
    request = factory.get(
        f'/dashboard_client/node_detail/{project.polygon_id}/{node.id}/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    # Mock user and client
    user = User.objects.filter(is_superuser=True).first() # Use superuser for setup
    # If the view requires client_required, let's mock request.user
    class MockUser:
        is_authenticated = True
        client = project.client
    request.user = MockUser()
    
    response = node_detail(request, project.polygon_id, node.id)
    print("Response Status:", response.status_code)
    print("Response Content:", response.content.decode('utf-8')[:1000])
else:
    print("Node chottmariemnode03 not found")
