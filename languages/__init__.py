import os
import importlib

def _import_submodules():
    BLACKLIST = ('__init__', 'base')
    for f in os.listdir(__path__[0]):
        if not f[-3:] == '.py':
            continue
        module_name = f[:-3]
        if module_name in BLACKLIST:
            continue
        _import_submodule(module_name)

def _import_submodule(name):
    import languages
    module = importlib.import_module('languages.' + name)
    setattr(languages, name, getattr(module, name))
    
def all():
    import languages
    import languages.base
    _import_submodules()
    found = []
    for key in dir(languages):
        item = getattr(languages, key)
        if isinstance(item, languages.base.Language):
            found.append(item)
    return found

def get(language_name):
    import languages
    try:
        _import_submodule(language_name)
        return getattr(languages, language_name)
    except AttributeError:
        for language in all():
            if language.name == language_name:
                return language
        raise Exception("No language named '{0}' found".format(language_name))
    except TypeError:
        return (get(n) for n in language_name)
        
