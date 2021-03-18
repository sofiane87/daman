from setuptools import setup, find_packages

setup(
    name="daman",
    python_requires=">=3.6.0",
    version="0.1",
    packages=find_packages("."),
    package_dir={"": "."},
    include_package_data=True,
    zip_safe=False,
)
