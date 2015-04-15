
from generic import Editable
from util import BinaryIO


class Furniture(Editable):
    """Furniture is like a spriteless overworld. The objects usually exist
    with the models placed on the map"""
    def define(self):
        self.uint16('script')
        self.uint16('u2')
        self.uint16('x')  # x
        self.uint16('pad_6', default=0)
        self.uint16('y')  # y
        self.uint16('ua')
        self.uint16('uc')
        self.uint16('ue')
        self.uint16('u10')
        self.uint16('u12')


class Overworld(Editable):
    """Interactable sprite present on a map"""
    def define(self):
        self.uint16('id')
        self.uint16('sprite')
        self.uint16('movement')
        self.uint16('u6')
        self.uint16('flag')
        self.uint16('script')
        self.uint16('uc')
        self.uint16('distance')  # activation dist. from front of sprite
        self.uint16('u10')
        self.uint16('u12')
        self.uint16('u14')
        self.uint16('u16')
        self.uint16('x')
        self.uint16('y')
        self.uint16('z')
        self.uint16('u1e')


class Warp(Editable):
    def define(self):
        self.uint16('x')
        self.uint16('y')
        self.uint16('map')
        self.uint16('anchor')
        self.uint16('pad_8', default=0)
        self.uint16('pad_a', default=0)


class Trigger(Editable):
    def define(self):
        self.uint16('script')
        self.uint16('x')  # topmost
        self.uint16('y')  # leftmost
        self.uint16('width', default=1)
        self.uint16('height', default=1)
        self.uint16('pad_a', default=0)
        self.uint16('uc')
        self.uint16('flag')


class ZoneEvents(Editable):
    def define(self, game):
        self.game = game
        self.uint32('num_furniture')
        # self.array('furniture', Furniture().base_struct)
        self.uint32('num_overworlds')
        # self.array('overworlds', Overworld().base_struct)
        self.uint32('num_warps')
        # self.array('warps', Warp().base_struct)
        self.uint32('num_triggers')
        # self.array('triggers', Trigger().base_struct)
        self.furniture = []
        self.overworlds = []
        self.warps = []
        self.triggers = []

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.num_furniture = reader.readUInt32()
        self.furniture = [Furniture(reader=reader)
                          for i in range(self.num_furniture)]
        self.num_overworlds = reader.readUInt32()
        self.overworlds = [Overworld(reader=reader)
                           for i in range(self.num_overworlds)]
        self.num_warps = reader.readUInt32()
        self.warps = [Warp(reader=reader) for i in range(self.num_warps)]
        self.num_triggers = reader.readUInt32()
        self.triggers = [Trigger(reader=reader)
                         for i in range(self.num_triggers)]
