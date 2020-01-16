__all__ = ["generate_info"]

import re

from typing import Mapping, Optional, Callable

VERSION_REGEX = re.compile(
    r'v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(-(?P<status>\w+))?')
SPECIAL_VERSION_NAMES = ["latest", "nightly", "stable"]


rule_sys = {"windows": "winnt"}
rules_os = {"windows": "win"}
rules_arch = {
    "i686": "x86",
    "x86_64": "x64",
    "ARMv8": "aarch64",
    "ARMv7": "armv7l"
}
rules_osarch = {
    "win-i686": "win32",
    "win-x86_64": "win64",
    "macos-x86_64": "mac64",
    "linux-ARMv7": "linux-armv7l",
    "linux-ARMv8": "linux-aarch64"
}
rules_extension = {
    "windows": "exe",
    "linux": "tar.gz",
    "macos": "dmg",
    "freebsd": "tar.gz"
}
rules_bit = {
    "i686": 32,
    "x86_64": 64,
    "ARMv8": 64,
    "ARMv7": 32,
}

VALID_SYSTEM = ["windows", "linux", "freebsd", "macos"]
VALID_OS = ["win", "linux", "freebsd", "macos"]
VALID_ARCHITECTURE = list(rules_arch.keys())
VALID_ARCH = list(rules_arch.values())


def identity(*args):
    return args[0] if len(args) == 1 else args


def no_validate(*args):
    return True


def is_system(system):
    return system in VALID_SYSTEM


def is_os(os):
    return os in VALID_OS


def is_architecture(arch):
    return arch in VALID_ARCHITECTURE


def is_arch(arch):
    return arch in VALID_ARCH


def is_version(version):
    if version in SPECIAL_VERSION_NAMES:
        return True
    else:
        return bool(VERSION_REGEX.match(version))


def is_valid_release(version, system, architecture):
    if (system == "windows"
            and architecture not in ["i686", "x86_64"]):
        return False
    if (system == "macos"
            and architecture not in ["x86_64"]):
        return False
    if (system == "freebsd"
            and architecture not in ["x86_64"]):
        return False
    if (version == "latest" and (
            architecture not in ["i686", "x86_64"]
            or system not in ["windows", "macos", "linux"])):
        return False
    return True


class NameFilter:
    def __init__(self,
                 f: Callable = identity,
                 rules: Optional[Mapping] = None,
                 validate: Callable = no_validate):
        self.f = f
        self.rules = rules if rules else {}
        self.validate = validate

    def __call__(self, *args):
        assert self.validate(*args)
        # a no-op if there's no rules
        return self.rules.get(self.f(*args), self.f(*args))


f_major_version = NameFilter(lambda x: x.lstrip('v').split('.')[0],
                             validate=is_version)
f_vmajor_version = NameFilter(lambda x: x.split('.')[0])
f_Vmajor_version = NameFilter(lambda x: f_vmajor_version(x).capitalize())
f_minor_version = NameFilter(lambda x: '.'.join(x.lstrip('v').
                                                split('.')[0:2]),
                             validate=is_version)
f_vminor_version = NameFilter(lambda x: '.'.join(x.split('.')[0:2]))
f_Vminor_version = NameFilter(lambda x: f_vminor_version(x).capitalize())
f_patch_version = NameFilter(lambda x: x.lstrip('v').split('-')[0],
                             validate=is_version)
f_vpatch_version = NameFilter(lambda x: x.split('-')[0])
f_Vpatch_version = NameFilter(lambda x: f_vpatch_version(x).capitalize())

f_version = NameFilter(validate=is_version)

f_system = NameFilter(validate=is_system)
f_System = NameFilter(f=lambda x: f_system(x).capitalize())
f_SYSTEM = NameFilter(f=lambda x: f_system(x).upper())

f_sys = NameFilter(rules=rule_sys, validate=is_system)
f_Sys = NameFilter(f=lambda x: f_sys(x).capitalize())
f_SYS = NameFilter(f=lambda x: f_sys(x).upper())

f_os = NameFilter(rules=rules_os, validate=is_system)
f_Os = NameFilter(f=lambda x: f_os(x).capitalize())
f_OS = NameFilter(f=lambda x: f_os(x).upper())

f_arch = NameFilter(rules=rules_arch, validate=is_architecture)
f_Arch = NameFilter(f=lambda x: f_arch(x).capitalize())
f_ARCH = NameFilter(f=lambda x: f_arch(x).upper())

f_osarch = NameFilter(f=lambda os, arch: f"{os}-{arch}",
                      rules=rules_osarch,
                      validate=lambda os, arch:
                      is_os(os)and is_architecture(arch))
f_Osarch = NameFilter(f=lambda os, arch: f_osarch(os, arch).capitalize())
f_OSarch = NameFilter(f=lambda os, arch: f_osarch(os, arch).upper())

f_bit = NameFilter(rules=rules_bit, validate=is_architecture)

f_extension = NameFilter(rules=rules_extension, validate=is_system)


def generate_info(plain_version: str,
                  system: str,
                  architecture: str,
                  **kwargs):
    os = f_os(system)
    arch = f_arch(architecture)

    configs = {
        "system": system,
        "System": f_System(system),
        "SYSTEM": f_SYSTEM(system),

        "sys": f_sys(system),
        "Sys": f_Sys(system),
        "SYS": f_SYS(system),

        "os": os,
        "Os": f_Os(system),
        "OS": f_OS(system),

        "architecture": architecture,

        "Arch": f_Arch(architecture),
        "arch": arch,
        "ARCH": f_ARCH(architecture),

        "osarch": f_osarch(os, architecture),
        "Osarch": f_Osarch(os, architecture),
        "OSarch": f_OSarch(os, architecture),

        "bit": f_bit(architecture),
        "extension": f_extension(system),

        "version": f_version(plain_version),
        "major_version": f_major_version(plain_version),
        "vmajor_version": f_vmajor_version(plain_version),
        "minor_version": f_minor_version(plain_version),
        "vminor_version": f_vminor_version(plain_version),
        "patch_version": f_patch_version(plain_version),
        "vpatch_version": f_vpatch_version(plain_version)
    }

    kwargs.update(configs)

    return kwargs