from setuptools import setup, find_packages
setup(
    name = "sesspy",
    version = "0.2.1",
    packages = find_packages(exclude=['tests']),
    install_requires = [],
    extras_require = {
        "sqlalchemy": ["sqlalchemy"],
    },
    package_data = {
        '': ['/COPYING', '/COPYING.LESSER'],
    },
    include_package_data=True,

    test_suite = "tests",
    tests_require = ["mock", "sqlalchemy"],

    author = "Mark Nevill",
    author_email = "mark@nevill.ch",
    description = "Session/Transaction Management and Dependency Injection",
    license = "LGPLv3",
    keywords = "session transaction dependency injection",
)
