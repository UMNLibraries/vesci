from pathlib import Path
import pytest
import shutil
import subprocess

from git import Repo
from git.util import rmtree

from vesci import vesci

def pytest_addoption(parser):
    parser.addoption(
        "--python-versions",
        action="store",
        required=True,
        help="python versions to use in tests"
    )

@pytest.fixture
def python_versions(request):
    versions = request.config.getoption("--python-versions").split(',')
    return versions

@pytest.fixture(scope="session", autouse=True)
def verify_dependencies():
    vesci.verify_dependencies()

@pytest.fixture(scope="session", autouse=True)
def tests_path():
    return Path(__file__).parent.resolve()

@pytest.fixture(scope="session", autouse=True)
def project_path(tests_path):
    return Path(tests_path / 'project')

@pytest.fixture(scope="session", autouse=True)
def fixtures_path(tests_path):
    return Path(tests_path / 'fixtures')

@pytest.fixture(scope="session", autouse=True)
def envs_path(fixtures_path):
    return Path(fixtures_path / 'envs')

@pytest.fixture(autouse=True)
def change_cwd(project_path, request, monkeypatch):
    monkeypatch.chdir(project_path)

@pytest.fixture(scope="session", autouse=True)
def git_repo(verify_dependencies, project_path, tests_path, envs_path):
    repo = Repo.init(project_path)

    env_path = Path(envs_path / 'main')
    shutil.copytree(env_path, project_path, dirs_exist_ok=True)
    repo.index.add([file_path.name for file_path in env_path.iterdir()])
    repo.index.commit('Adds env files to force GitPython to properly initialize the repo.')

    branch_names = [branch.name for branch in repo.branches]
    if 'main' not in branch_names:
        repo.git.branch('main')
    repo.git.checkout('main')
    if 'master' in branch_names:
        repo.git.branch('-D', 'master')

    yield repo

    rmtree(project_path)
