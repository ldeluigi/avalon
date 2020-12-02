from configparser import ConfigParser
from importlib import resources

import text


class FormatString(str):
    defaults: dict = dict()

    def __call__(self, *args, **kwargs):
        return self.format(*args, **{**self.defaults, **kwargs})


class StringSet():

    def __init__(self, package, resource):
        self._package = package
        self._resource = resource
        self._templates = None
        self._defaults = dict()

    def __getattr__(self, key):
        return self._get_templates()[key.lower()]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            key = "_".join(key)
        return self._get_templates()[key.lower()]

    def _load_templates(self):
        conf = ConfigParser()
        with resources.open_text(self._package, self._resource) as f:
            conf.read_file(f)

        def _newFormatString(tmpl):
            f = FormatString(tmpl.replace("\\n", "\n"))
            f.defaults = self._defaults
            return f
        return {key: _newFormatString(tmpl) for key, tmpl in conf["strings"].items()}

    def _get_templates(self):
        if self._templates is None:
            self._templates = self._load_templates()
        return self._templates

    def withDefaults(self, **kwargs):
        s = StringSet(self._package, self._resource)
        s._defaults = {**self._defaults, **kwargs}
        return s


StringSets = {
    name: StringSet(text, name + ".ini")
    for name in ["avalon-en-base", "avalon-it-base", "avalon-en-starwars", "avalon-it-starwars"]
}
