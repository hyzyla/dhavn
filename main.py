from compose.cli.command import get_project
from compose.project import Project, Service, Container
from compose.network import Network
from pprint import pprint

project = get_project(project_dir='example')
redis: Service = project.get_service(name='redis')
# pprint(redis.__dict__)
new_redis = Service(
    name='new_redis',
    client=redis.client,
    default_platform=redis.default_platform,
    project=redis.project,
    **redis.options,
)
project.services.append(new_redis)
print(project.create('new_redis'))
