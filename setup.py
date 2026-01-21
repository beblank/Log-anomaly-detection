"""Setup file for the Multi-Tenant ML SaaS Platform."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ml-saas-platform",
    version="0.1.0",
    author="beblank",
    description="Multi-Tenant ML SaaS Platform for Log Anomaly Detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/beblank/Log-anomaly-detection",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ml-saas=src.app.main:main",
        ],
    },
)
