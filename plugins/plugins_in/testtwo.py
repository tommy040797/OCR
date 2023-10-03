"""
PLugin2
"""


class Plugin:
    def __init__(self, name) -> None:
        self.name = name

    def foo(self):
        print(self.name, "plugin2")
