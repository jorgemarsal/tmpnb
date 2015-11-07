import jinja2
import json
import os

from pykube.config import KubeConfig
from pykube.http import HTTPClient

class KubernetesError(Exception):
    pass

class KubernetesApi(object):
    def __init__(self,filename):
        self.config = KubeConfig(filename)
        self.http_client = HTTPClient(self.config)

    def get_pods(self):
        """Returns a list of the pod names"""
        return self._get_components('pods')

    def get_replication_controllers(self):
        """Returns a list of the rc names"""
        return self._get_components('replicationcontrollers')

    def get_services(self):
        """Returns a list of the service names"""
        return self._get_components('services')

    def start_pod(self, *args, **kwargs):
        filename = '{}/templates/pod.json'.format(os.path.dirname(__file__))
        with open(filename) as f:
            t = jinja2.Template(f.read())
        json_str = t.render(
            podname=kwargs.get('podname'),
            containername=kwargs.get('containername'),
            containerimage=kwargs.get('containerimage'),
            imagepullpolicy=kwargs.get('imagepullpolicy'),
            restartpolicy=kwargs.get('restartpolicy'),
            command=kwargs.get('command')
        )
        json_obj = json.loads(json_str)
        rsp = self.http_client.post(url='/pods', json=json_obj)
        if rsp.status_code != 201: raise KubernetesError


    def _get_components(self, component_type):
        rsp = self.http_client.get(url='/{}'.format(component_type))
        if rsp.status_code != 200: raise KubernetesError
        json_rsp = json.loads(rsp.text)
        if 'items' in json_rsp:
            items = [x['metadata']['name'] for x in json_rsp['items']]
            return items
        raise KubernetesError


'''
apiVersion: v1
clusters:
- cluster:
    insecure-skip-tls-verify: true
    server: http://127.0.0.1:8080
  name: local
contexts:
- context:
    cluster: local
    user: jorgemarsal
  name: local
current-context: local
kind: Config
preferences: {}
users:
- name: jorgemarsal
  user:
    token: "123"
'''
k = KubernetesApi('/home/jorgem/.kube/config')
for item in k.get_pods():
    print(item)
for item in k.get_replication_controllers():
    print(item)
for item in k.get_services():
    print(item)

k.start_pod(podname='busybox',
            containername='busybox',
            containerimage='busybox',
            imagepullpolicy='IfNotPresent',
            restartpolicy='Always',
            command=['"sleep"', '"3600"']
)


