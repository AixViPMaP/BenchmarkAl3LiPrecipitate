from functools import wraps
import inspect

from ipywidgets import widgets

def widget_property(f):
    @wraps(f)
    def wrapfunc(self):
        try:
            return self.__widgets__[f.__name__]
        except KeyError:
            args=[]
            if len(inspect.getargspec(f).args)>=1:
                args=[self,]
            wdgt = f(*args)
            default_value =  self.__default__.get(f.__name__)
            if default_value and hasattr(wdgt,'value'):
                wdgt.value = default_value
            return self.__widgets__.setdefault(f.__name__, wdgt)
    return property(wrapfunc)

class IpyApp:
    __widget_name_prefix = 'w'
    def __init__(self, default_value={}):
        self.__widgets__ = {}
        self.__default__ = default_value

    def create_Accordion(self, titles, vboxes):
        vboxes = [ widgets.VBox(i) for i in vboxes]
        tab = widgets.Accordion(children=vboxes)
        for i, title in enumerate(titles):
            tab.set_title(i, title)
        return tab

    def get_widget_values(self):
        params={
            n: wdgt.value
            for n, wdgt in self.__widgets__.items()
            if isinstance(wdgt, widgets.ValueWidget) and n.startswith(self.__widget_name_prefix) and hasattr(wdgt, 'value')
        }
        return params