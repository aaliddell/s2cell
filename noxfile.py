import nox


nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ['bandit', 'coverage', 'flake8', 'pylint', 'pydocstyle']


@nox.session()
def bandit(session):
    session.install('.[dev]')
    session.run('bandit', '-r', 's2cell', *session.posargs)

@nox.session()
def coverage(session):
    session.install('.[dev]')
    session.run(
        'pytest', '--import-mode=importlib', '--cov=s2cell', '--cov-report', 'term-missing',
        '--cov-branch', '--cov-fail-under=100', '-n', 'auto', '--instafail', *session.posargs
    )

@nox.session()
def flake8(session):
    session.install('.[dev]')
    session.run('flake8', 's2cell', 'tests', *session.posargs)

@nox.session()
def pylint(session):
    session.install('.[dev]')
    session.run('pylint', 's2cell', *session.posargs)

@nox.session()
def pydocstyle(session):
    session.install('.[dev]')
    session.run('pydocstyle', 's2cell', *session.posargs)

@nox.session()
def test(session):
    session.install('.[dev]')
    session.run('pytest', '--import-mode=importlib', '-n', 'auto', '--instafail', *session.posargs)

@nox.session()
def build_wheel(session):
    session.install('wheel')
    session.run('python', 'setup.py', 'bdist_wheel')

@nox.session()
def upload_release(session):
    # Add requirements for building wheel and uploading to PyPI
    session.install('wheel', 'twine')

    # Clear out old dist files if they exist
    session.run('rm', '-rf', 'dist', external=True)

    # Build sdist and wheel
    session.run('python', 'setup.py', 'sdist', 'bdist_wheel')

    # Check description with twine
    session.run('twine', 'check', 'dist/*')

    # Upload to PyPI
    session.run('twine', 'upload', '-r' , 'testpypi', 'dist/*')  # TODO: remove test repo
