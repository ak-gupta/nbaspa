#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    README = readme_file.read()

REQUIREMENTS = [
    "alive-progress>=1.6.2,<=1.6.2",
    "Click>=7.1.2,<=7.1.2",
    "fsspec>=0.8.5,<=0.8.5",
    "hyperopt>=0.2.5,<=0.2.5",
    "lifelines>=0.25.9,<=0.25.9",
    "lightgbm>=3.1.1,<=3.1.1",
    "matplotlib>=3.3.4,<=3.3.4",
    "pandas>=1.2.1,<=1.2.1",
    "prefect>=0.14.5,<=0.14.5",
    "ratelimit>=2.2.1,<=2.2.1",
    "requests>=2.25.1,<=2.25.1",
    "scikit-learn>=0.24.1,<=0.24.1",
    "shap[plots]>=0.39.0,<=0.39.0",
    "seaborn>=0.11.1,<=0.11.1",
    "xgboost>=1.3.3,<=1.3.3"
]

EXTRAS_REQUIRE = {
    "tests": ["pytest", "pytest-cov"],
    "docs": ["sphinx", "furo"],
    "qa": [
        "black",
        "flake8",
        "mypy",
        "pip-tools",
        "types-requests",
        "types-click"
    ],
}
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["docs"] + EXTRAS_REQUIRE["qa"]

setup(
    author="Akshay Gupta",
    author_email='akgcodes@gmail.com',
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    description="Survival analysis-based win percentage and player impact",
    install_requires=REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    license="MIT license",
    long_description=README,
    include_package_data=True,
    keywords="nbaspa",
    name="nbaspa",
    packages=find_packages(include=["nbaspa", "nbaspa.*"]),
    url="https://github.com/ak-gupta/nbaspa",
    version="0.1.0",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "nbaspa-download=nbaspa.data.scripts.download:download",
            "nbaspa-clean=nbaspa.data.scripts.clean:clean",
            "nbaspa-model=nbaspa.model.scripts.model:model",
            "nbaspa-rate=nbaspa.player_rating.scripts.rate:rate"
        ],
    },
)
