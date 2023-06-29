from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'azplocal',
    version = '0.0.3',
    author = 'Amal Abey',
    author_email = 'amalabey@gmail.com',
    license = 'MIT',
    description = 'Validate, run and debug Azure Pipelines on local machine',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/amalabey/azp-local-runner',
    py_modules = ['azplocal_tool', 'app'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    package_data={'css': ['app/app.css']},
    entry_points = '''
        [console_scripts]
        azplocal=azplocal_tool:cli
    '''
)