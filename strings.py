from configparser import ConfigParser
from importlib import resources

import text


class FormatString(str):

    def __call__(self, *args, **kwargs):
        return self.format(*args, **kwargs)


class StringSet:

    def __init__(self, package, resource):
        self._package = package
        self._resource = resource
        self._templates = None

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
        return {key: FormatString(tmpl.replace("\\n", "\n"))
                for key, tmpl in conf["strings"].items()}

    def _get_templates(self):
        if self._templates is None:
            self._templates = self._load_templates()
        return self._templates


StringSets = {
    name: StringSet(text, name + ".ini")
    for name in ["avalon-en-base"]
}
