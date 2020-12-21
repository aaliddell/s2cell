import nox


nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True


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
