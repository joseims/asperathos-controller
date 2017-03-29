from service.api.actuator.basic_actuator import Basic_Actuator
from service.api.actuator.instance_locator import Instance_Locator
from service.api.actuator.remote_kvm import Remote_KVM

# TODO: documentation
class Actuator_Builder:

    def get_actuator(self, name):
        if name == "basic":
            instance_locator = Instance_Locator()
            remote_kvm = Remote_KVM()
            return Basic_Actuator(instance_locator, remote_kvm)
        else:
            raise Exception("Unknown actuator type")