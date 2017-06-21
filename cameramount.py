import abc
from solid import *
from solid.utils import *

class CameraMount(object):
    __metaclass__ = abc.ABCMeta

    VERSION = 1

    SEGMENTS = 12 

    INFINITE = 50

    def __init__(self, name, camera, vtx, fc):
        self.name = name
        self.camera = camera
        self.vtx = vtx
        self.fc = fc

    @abc.abstractmethod
    def asm(self):
        """ Assemble and return the part """
        return

    @abc.abstractmethod
    def test(self):
        """ Test with other components """
        return

    def build(self):
        """Build the part returned by asm and write to scad"""
        filepath = "build/{}-v{}.scad".format(self.name, CameraMount.VERSION)
        header = "$fn = {};".format(CameraMount.SEGMENTS)
        scad_render_to_file(self.asm(),  filepath = filepath, file_header=header)


