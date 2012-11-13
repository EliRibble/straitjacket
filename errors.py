class StraitjacketError(Exception):
    pass
class InputError(StraitjacketError):
    pass
class ConfigError(StraitjacketError):
    pass
class LanguageInitError(ConfigError):
    pass
class AppArmorProtectionFailure(StraitjacketError):
    pass

