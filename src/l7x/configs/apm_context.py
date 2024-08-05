######################################################################################

from os import getenv
from typing import NamedTuple

######################################################################################

class ApmContext(NamedTuple):
    KUBERNETES_POD_SERVICE_ACCOUNT: str | None
    KUBERNETES_NODE_IP: str | None
    KUBERNETES_POD_IP: str | None
    KUBERNETES_NODE_NAME: str | None
    KUBERNETES_NAMESPACE: str | None
    KUBERNETES_POD_NAME: str | None
    KUBERNETES_POD_UUID: str | None

######################################################################################

def get_apm_context() -> ApmContext:
    return ApmContext(
        KUBERNETES_POD_SERVICE_ACCOUNT=getenv('KUBERNETES_POD_SERVICE_ACCOUNT'),
        KUBERNETES_NODE_IP=getenv('KUBERNETES_NODE_IP'),
        KUBERNETES_POD_IP=getenv('KUBERNETES_POD_IP'),
        KUBERNETES_NODE_NAME=getenv('KUBERNETES_NODE_NAME'),
        KUBERNETES_NAMESPACE=getenv('KUBERNETES_NAMESPACE'),
        KUBERNETES_POD_NAME=getenv('KUBERNETES_POD_NAME'),
        KUBERNETES_POD_UUID=getenv('KUBERNETES_POD_UUID'),
    )

######################################################################################
