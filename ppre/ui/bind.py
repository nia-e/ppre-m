"""Data binder used to ensure two objects have the same values"""

from util import hook


class Bind(object):
    def __init__(self, container, key, parent=None, attr=None):
        print('Bind', container.name, key)
        self.container = container
        self.key = key
        self.parent = self.container if parent is None else parent
        self.attr = self.key if attr is None else attr
        parent.__setattr__ = hook.multi_call_patch(parent.__setattr__)
        parent.__setattr__.add_call(self.on_parent_attr_set)
        container.__setitem__ = hook.multi_call_patch(container.__setitem__)
        container.__setitem__.add_call(self.on_container_key_set)

        self.interface = self.container[self.key]
        self.model = getattr(self.parent, self.attr)
        self.bind_children()
        self.on_container_key_set(None, self.key, self.interface, True)
        self.on_parent_attr_set(None, self.attr, self.model, True)

    def bind_children(self):
        # TODO: clear binding
        for child_key in self.interface.keys():
            print(child_key)
            if hasattr(self.model, child_key):
                self.interface.bind(child_key, self.model)

    def unbind(self):
        for child_key in self.interface.keys():
            self.interface.unbind(child_key)
        self.parent.__setattr__ = hook.restore(self.parent.__setattr__)
        self.container.__setitem__ = hook.restore(self.container.__setitem__)

    def on_container_key_set(self, res, name, interface, init=False):
        print('cks', name, interface.name)
        if name != self.key:
            return res
        if interface == self.interface and not init:
            return res
        interface.ui.set_value = interface.set_value = \
            hook.multi_call_patch(interface.ui.set_value)
        interface.set_value.add_call(self.on_interface_value_set)
        self.interface = interface
        self.bind_children()
        return res

    def on_interface_value_set(self, res, value):
        print('ivs', self.key, self.attr, value, self.interface.get_value())
        if getattr(self.parent, self.attr) != value:
            setattr(self.parent, self.attr, value)
        return res

    def on_parent_attr_set(self, res, name, value, init=False):
        print('pas', name, value)
        if name != self.attr:
            return res
        if value == self.model and not init:
            return res
        try:
            value.__setattr__ = hook.multi_call_patch(value.__setattr__)
            value.__setattr__.add_call(self.on_model_attr_set)
        except AttributeError:
            # "values" can't have their __setattr__ modified
            self.interface.set_value(value)
        self.model = value
        self.bind_children()
        return res

    def on_model_attr_set(self, res, name, value):
        print(name, value)
        if name in self.interface:
            if self.interface[name].get_value() != value:
                self.interface[name].set_value(value)
        return res


def bind(interface, key, container=None, attr=None):
    """Ensures consistency between interface[key] and container.attr
    """
    if attr is None:
        attr = key
    if container is None:
        container = interface
    # interface[key].value

    def on_container_attr_set(res, name, value):
        if name != attr:
            return res
        return res
    container.__setattr__ = hook.multi_call_patch(container.__setattr__)
    container.__setattr__.add_call(on_container_attr_set)

    def on_interface_key_set(res, name, sub_if):
        if name != key:
            return res

        def on_set_value(res, new_value):
            return res
        sub_if.set_value = hook.multi_call_patch(sub_if.set_value)
        sub_if.set_value.add_call(on_set_value)
        return res
    interface.__setitem__ = hook.multi_call_patch(interface.__setitem__)
    interface.__setitem__.add_call(on_interface_key_set)
    on_interface_key_set(None, key, interface[key])