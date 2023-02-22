# te

![pypi_badge](https://img.shields.io/pypi/v/te?label=PyPI&logo=pypi) ![readthedocs_badge](https://img.shields.io/readthedocs/te?label=Read%20the%20Docs&logo=read-the-docs) ![badge](https://copr.fedorainfracloud.org/coprs/g/freeipa/neoave/package/te/status_image/last_build.png)

Executrix is a general multi-host workload execution utility.

It's intentionally lightweight, utilizing existing technology like Ansible
for execution and Mrack for provisioning.

Primary use cases are:

- repeatable test execution which combines provisioning of vms/containers and
  test execution
- preparation of vms for labs/workshops
- preparation of development environment

## Installation

te can be installed via pip, from [PyPI](https://pypi.org/project/te/):

```bash
pip install te
```

It is also available for Fedora 37+ via [COPR](https://copr.fedorainfracloud.org/coprs/g/freeipa/neoave/package/te/):

```
sudo dnf copr enable @freeipa/neoave
sudo dnf install te
```

## Run

```bash
$ te run
# runs all phases

$ te run --phase my-phase-name
# runs only this phase

$ te run --upto some-other-phase
# runs all phases from beginning upto the defined one (including)
```

## Contribute

Projects is using [black](https://github.com/psf/black) formatter and [isort](https://github.com/PyCQA/isort) to keep consistent
formatting, [flake8](https://flake8.pycqa.org/en/latest/) and
[pydocstyle](http://pycodestyle.pycqa.org/en/latest/intro.html) to ensure following
Python good practices.

Contributions (Pull Requests) are welcome. It is expected that they will pass tox tests and code checkers.
Inclusion of the unit tests for the new code is recommended.
Because of that we have configured [pre-commit](https://pre-commit.com/) hook.
Please enable the feature on your local system and use it before sending a patch.
It could save us lot of re-pushing to the PR.

### Black formatting and isort
Expected formatting can be achieved by running:
```
$ make format
```

Look into [black](https://github.com/psf/black) documentation for possible integration
in editors/IDEs.

### Testing
Just run tox to execute all tests and linters

```
$ tox
# or use make
$ make test
```
