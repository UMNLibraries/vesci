from pathlib import Path
import pytest
import subprocess

import git

from vesci import vesci

@pytest.mark.order(1)
def test_tool_is_available():
    assert vesci.tool_is_available('git')
    assert not vesci.tool_is_available('bogus')

@pytest.mark.order(2)
def test_is_project_root_path(project_path):
    assert vesci.is_project_root_path(project_path)
    assert not vesci.is_project_root_path(Path('/'))

@pytest.mark.order(3)
def test_find_project_root_path(project_path, change_cwd):
    project_path_str = str(project_path)
    assert str(vesci.find_project_root_path()) == project_path_str

@pytest.mark.order(4)
def test_project_root_path(project_path, change_cwd):
    project_path_str = str(project_path)
    assert str(vesci.project_root_path(project_path)) == project_path_str
    assert str(vesci.project_root_path(str(project_path))) == project_path_str
    assert str(vesci.project_root_path()) == project_path_str

@pytest.mark.order(5)
def test_get_git_repo(project_path):
    assert isinstance(vesci.get_git_repo(project_path), git.Repo)

@pytest.mark.order(6)
def test_venvs_path(project_path):
    venvs_path = vesci.venvs_path(project_path)
    assert venvs_path.exists() and venvs_path.is_dir()

@pytest.mark.order(7)
def test_get_python_executable_path(project_path, python_versions):
    for version in python_versions:
        assert subprocess.run(
            [
                vesci.get_python_executable_path(project_path, version),
                '--version'
            ],
            capture_output=True,
            text=True
        ).stdout == f'Python {version}\n'

def test_parse_venv_config(fixtures_path):
    assert vesci.parse_venv_config(Path(fixtures_path / 'pyvenv.cfg')) == {
        'python': '/home/foo/.anyenv/envs/pyenv/versions/3.7.2/bin',
        'version': '3.7.2',
    }

