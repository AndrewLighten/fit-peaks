from setuptools import setup, find_packages

setup(
    name="fitpeaks",
    version="1.0",
    packages=find_packages(),
    scripts=["fitpeaks.py"],
    # metadata to display on PyPI
    author="Andrew Lighten",
    author_email="andrew@digital-ironworks.com",
    description="Fitness Peaks",
    long_description="A tool for loading and displaying fitness peaks",
    keywords="fitpeaks",
    classifiers=[
        "Environment :: Console",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.8",
        "Natural Language :: English",
    ],
    entry_points={"console_scripts": ["fitpeaks = fitpeaks:main",],},
    python_requires=">=3.8",
    license="https://www.apache.org/licenses/LICENSE-2.0",
    url="https://github.com/AndrewLighten/fit-peaks",
    platforms=[
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=["Click>=7.0", "termcolor>=1.1.0", "fitparse>=1.1.0", "zwift-client>=0.2.0"],
)
