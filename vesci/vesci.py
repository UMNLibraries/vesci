from configparser import ConfigParser
import os
from pathlib import Path
import pprint
import subprocess
import venv

import click
from git import Repo, InvalidGitRepositoryError

tool_dependencies=['git','poetry','pyenv']

def tool_is_available(tool):
    result = subprocess.run(['which', tool], stdout=subprocess.PIPE)
    return True if result.returncode == 0 else False

def verify_dependencies(tool_dependencies=tool_dependencies):
    if not all(map(lambda tool: tool_is_available(tool), tool_dependencies)):
        raise Exception

def parent_paths(path, paths=None):
    paths = [] if paths is None else paths
    paths.append(path)
    # The root of the filesystem will not have a name.
    if path.name:
        parent_paths(path.parent, paths)
    return paths

def is_project_root_path(path):
    return (
        True
        if Path(path / '.git').exists() and Path(path / '.git').is_dir()
        else False
    )

def find_project_root_path():
    return next(
        filter(is_project_root_path, parent_paths(Path.cwd())),
        Path.cwd()
    )

def project_root_path(root=None):
    path = None
    if root:
        if isinstance(root, Path):
            path = root
        elif isinstance(root, str):
            path = Path(root)
        else:
            raise Exception
        if not is_project_root_path(path):
            raise Exception
    else:
        path = find_project_root_path()
    return path

#project_root_path = find_project_root_path()
#repo = Repo(project_root_path)
venvs_root_name = '.venvs'
#venvs_root_path = project_root_path / venvs_root_name
#venv_paths = list(filter(lambda child: child.is_dir(), venvs_root_path.iterdir()))
#venv_names = list(map(lambda path: path.name, venv_paths))

def parse_venv_config(venv_config_path):
    parser = ConfigParser()
    with open(str(venv_config_path)) as stream:
        # ConfigParser is for INI files, and requires a section header.
        parser.read_string("[dummy_section]\n" + stream.read())
        config = dict(parser.items('dummy_section'))
        return {
            'python': config['home'],
            'version': config['version'],
        }

def get_git_repo(project_root_path):
    git_repo = None
    try:
        git_repo = Repo(project_root_path)
    except InvalidGitRepositoryError:
        print(f'Directory {path} is not a git repository')
    return git_repo

def get_env_info(name, project_info):
    env_info = {
        'git_branch': (name in project_info['git_branch_names']),
    }
    if name in project_info['venv_names']:
        env_info['venv'] = parse_venv_config(project_info['venvs_root_path'] / name / 'pyvenv.cfg')
    return env_info

def get_project_info(root=None):
    info = {
        'project_root_path': Path(root) if root else find_project_root_path()
    }
    #info['git_repo'] = Repo(info['project_root_path'])
    info['git_repo'] = get_git_repo(info['project_root_path'])
    info['git_branch_names'] = list(map(lambda branch: branch.name, info['git_repo'].branches)) if info['git_repo'] else []
    info['git_branch_active'] = info['git_repo'].active_branch.name if info['git_repo'] else None
    info['pyenv_root_path'] = Path(os.environ.get('PYENV_ROOT')) if os.environ.get('PYENV_ROOT') else None
    info['pyenv_versions_paths'] = list(filter(lambda child: child.is_dir(), (info['pyenv_root_path'] / 'versions').iterdir())) 
    info['pyenv_versions'] = list(map(lambda path: path.name, info['pyenv_versions_paths']))
#    info['venvs_root_path'] = Path(info['project_root_path'] / venvs_root_name) if Path(info['project_root_path'] / venvs_root_name).exists() else Path.mkdir(info['project_root_path'] / venvs_root_name)
#    info['venv_active_path'] = Path(os.environ.get('VIRTUAL_ENV')) if os.environ.get('VIRTUAL_ENV') else None
#    info['venv_active_name'] = info['venv_active_path'].name if info['venv_active_path'] else None
#    info['venv_paths'] = list(filter(lambda child: child.is_dir(), info['venvs_root_path'].iterdir()))
#    info['venv_names'] = list(map(lambda path: path.name, info['venv_paths']))
#    info['envs'] = {name: get_env_info(name, info) for name in list(set(info['venv_names']).union(info['git_branch_names']))}
    return info

@click.group()
def cli():
    pass

@cli.command('project-root')
def project_root():
    click.echo(str(find_project_root_path()))

@cli.command()
@click.option('--root', help='Project root directory.')
def ls(root: str):
    #click.echo(repo.branches)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(get_project_info(root))

def get_python_executable_path(project_path_root, python_version):
    info = get_project_info(str(project_path_root))
    if python_version in info['pyenv_versions']:
        return Path(info['pyenv_root_path'] / 'versions' / python_version / 'bin' / 'python')
    else:
        return None

def venvs_path(project_root_path, venvs_dirname=venvs_root_name):
    venvs_root_path = Path(project_root_path / venvs_dirname)
    if not venvs_root_path.exists():
        Path.mkdir(venvs_root_path)
    if venvs_root_path.exists() and not venvs_root_path.is_dir():
        raise Exception
    return venvs_root_path

def context(root=None):
    info = {
        'project_root_path': project_root_path(root)
    }
    #info['git_repo'] = Repo(info['project_root_path'])
    info['git_repo'] = get_git_repo(info['project_root_path'])
    info['git_branch_names'] = list(map(lambda branch: branch.name, info['git_repo'].branches)) if info['git_repo'] else []
    info['git_branch_active'] = info['git_repo'].active_branch.name if info['git_repo'] else None
    info['pyenv_root_path'] = Path(os.environ.get('PYENV_ROOT')) if os.environ.get('PYENV_ROOT') else None
    info['pyenv_versions_paths'] = list(filter(lambda child: child.is_dir(), (info['pyenv_root_path'] / 'versions').iterdir())) 
    info['pyenv_versions'] = list(map(lambda path: path.name, info['pyenv_versions_paths']))
#    info['venvs_root_path'] = Path(info['project_root_path'] / venvs_root_name) if Path(info['project_root_path'] / venvs_root_name).exists() else Path.mkdir(info['project_root_path'] / venvs_root_name)
#    info['venv_active_path'] = Path(os.environ.get('VIRTUAL_ENV')) if os.environ.get('VIRTUAL_ENV') else None
#    info['venv_active_name'] = info['venv_active_path'].name if info['venv_active_path'] else None
#    info['venv_paths'] = list(filter(lambda child: child.is_dir(), info['venvs_root_path'].iterdir()))
#    info['venv_names'] = list(map(lambda path: path.name, info['venv_paths']))
#    info['envs'] = {name: get_env_info(name, info) for name in list(set(info['venv_names']).union(info['git_branch_names']))}
    return info

def ensure_venv_exists(name, project_root_path, python_version):
    info = get_project_info(str(project_path_root))
    python_executable_path = get_python_executable_path(project_path_root, python_version)
    if name not in info['venv_names']:
        subrpocess.run(
            str(python_executable_path),
            '-m',
            'venv',
            str(info['venvs_root_path'] / name),
        )

def new_env(name, project_root_path, python_version):
    ensure_venv_exists(name, project_root_path, python_version)

@cli.command()
@click.option('--root', help='Project root directory')
@click.option('--version', help='Python version')
@click.argument('name')
def new(name, root):
    info = get_project_info(root)
    if name not in info['venv_names']:
#        venv.create(
#            info['venvs_root_path'] / name,
#            symlinks=True,
#            with_pip=True
#        )
        subrpocess.run(
            'python',
            '-m',
            'venv',
            str(info['venvs_root_path'] / name),
        )

def venv_activated():
    if os.environ['VIRTUAL_ENV']:
        click.echo('A virtual environment is activated, which must be manually deactivated before using a different environment.')
        click.confirm('Do you want to continue?', abort=True)

@cli.command()
@click.argument('name')
def use(name):
    venv_activated()
    click.echo('User did not abort.')
