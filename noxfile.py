import nox


nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ['coverage', 'docs', 'flake8', 'pylint', 'pydocstyle']


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
def docs(session):
    session.install('.[dev]')
    session.run(
        'sphinx-apidoc', '--no-toc', '--force', '--separate', '-o', 'docs/source/api', 's2cell'
    )
    session.run(
        'python', '-m', 'sphinx',
        '-c', 'docs/',
        '-a', # Update all output files
        '-E', # Do not reuse environment from previous run
        '-T', # Show full trace on error
        '-W', # Treat warnings as errors
        '--keep-going', # When using -W, only exit after all warnings shown
        #'-j', 'auto', # Generate in parallel
        'docs/source', 'docs/build',
    )

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
    session.run('twine', 'upload', 'dist/*')
