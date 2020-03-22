from compose.cli.command import get_project
from compose.project import Project, Service, Container
from compose.network import Network
from pprint import pprint

project = get_project(project_dir='example')
web: Service = project.get_service(name='web')
print(web)

redis: Service = project.get_service(name='redis')
print(redis.options)
