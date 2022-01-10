# vesci

Virtual Environment and Source Control Integration for Python. Supports poetry, pyenv, and git.

Highly experimental. Not even alpha software yet.

## Testing

Run the following, with your own Python versions installed via pyenv.

`pytest tests/test_vesci.py --python-versions 3.10.0,3.7.2`

## Notes

* Use in-project venvs!

* use case: manual venv switching
  * create first venv
    * python -m venv .venvs/main
    * source .venvs/main/bin/activate
    * poetry install
  * create second venv
    * mkdir .venvs/main/.poetry/
    * mv poetry.lock pyproject.toml .venvs/main/.poetry/
    * python -m venv .venvs/new-dep
    * deactivate - SHELL
    * source .venvs/new-dep/bin/activate - SHELL
    * add dependency to pyproject.toml
    * poetry install
  * switch back to first venv
    * mkdir .venvs/new-dep/.poetry/
    * mv poetry.lock pyproject.toml .venvs/new-dep/.poetry/
    * cp .venvs/main/.poetry/\* .
    * deactivate - SHELL
    * source .venvs/main/bin/activate - SHELL

* use case: manual venv+git branch switching
  * create first venv+git branch
    * python -m venv .venvs/main
    * source .venvs/main/bin/activate - SHELL
    * poetry install
    * git init
    * create .gitignore with .python-version and .venv\*
    * git add .gitignore poetry.lock pyproject.toml 
    * git commit
  * create second venv+git branch
    * git chekcout -b new-dep
    * mkdir .venvs/main/.poetry/
    * mv poetry.lock pyproject.toml .venvs/main/.poetry/
    * python -m venv .venvs/new-dep
    * deactivate - SHELL
    * source .venvs/new-dep/bin/activate - SHELL
    * add dependency to pyproject.toml
    * poetry install
  * switch back to first venv+git branch
    * mkdir .venvs/new-dep/.poetry/
    * cp poetry.lock pyproject.toml .venvs/new-dep/.poetry/
    * git add poetry.lock pyproject.toml
    * git commit
    * git checkout main
    * deactivate - SHELL
    * source .venvs/main/bin/activate - SHELL

* parameters:
  * python version (optional):
    * if missing, use parent branch python version
  * use parent branch packages?
    * Only relevant if the python version is the same as the parent branch version
  * git branch name

* boolean conditions:
  * pyenv-installed
  * valid-python-version
  * python-version-installed
  * git-installed
  * git-branch-exists

* algorithm
  * if branch already exists:
    * git checkout branch
  * else:
    * git create branch
  * use parent branch python version?
    * if yes:
      * do nothing
    * else:
      * get python version from user
      * if python version already installed:
        * do nothing
      * else:
        * search for python version in pyenv list
        * if found:
          * install python version with pyenv
        * else:
          * display error message
          * abort
        * pyenv local python version
        * set python version in pyproject.toml
  * use parent branch packages?
    * if yes:
      * cp -rp .venv 


