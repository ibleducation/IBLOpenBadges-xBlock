"""Setup for iblstudiosbadges XBlock."""

import os
from setuptools import setup


"""
Generic function to find package_data.

All of the files under each of the `roots` will be declared as package
data for package `pkg`.

"""
def package_data(pkg, roots):
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='iblstudiosbadges-xblock',
    version='0.9',
    description='iblstudiosbadges XBlock',
    packages=[
        'iblstudiosbadges',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'iblstudiosbadges = iblstudiosbadges:IBLstudiosbadges',
        ]
    },
    package_data=package_data("iblstudiosbadges", ["static", "public"]),
)
