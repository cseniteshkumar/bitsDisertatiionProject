from setuptools import setup, find_packages


setup(
    name="bits_dissertation_project",
    version="0.0.0",
    packages=find_packages(exclude=("tests", "docs", ".venv", "venv")),
    include_package_data=True,
    description="Dissertation project workspace - editable install helper",
)
