# Copyright 2022 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""executrix setup"""
# -*- coding: utf-8 -*-
import re
import sys

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as req:
    reqs = req.readlines()

with open("src/executrix/version.py", "r") as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE)
    if version is None:
        sys.stderr.write("Could not parse the version string.\n")
        sys.exit(1)

    executrix_version = version.group(1)

setup(
    name="executrix",
    version=executrix_version,
    description="General multi-host workload execution utility",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Petr Vobornik",
    author_email="pvoborni@redhat.com",
    url="https://github.com/neoave/executrix",
    license="Apache License 2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=reqs,
    scripts=["scripts/executrix"],
)
