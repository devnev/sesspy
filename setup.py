from setuptools import setup, find_packages
setup(
    name = "sesspy",
    version = "0.3.1",
    url = "http://nevill.ch/sesspy/",

    packages = find_packages(exclude=['tests']),
    install_requires = [],
    extras_require = {
        "sqlalchemy": ["sqlalchemy"],
    },
    package_data = {
        '': [
            '/COPYING', '/COPYING.LESSER',
            '/README.rst',
        ],
    },
    include_package_data=True,

    test_suite = "tests",
    tests_require = ["mock", "sqlalchemy"],

    author = "Mark Nevill",
    author_email = "mark@nevill.ch",
    description = "Session/Transaction Management and Dependency Injection",
    license = "LGPLv3",
    keywords = "session transaction dependency injection",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
)
