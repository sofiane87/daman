from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fr:
    requirements = fr.read().splitlines()

setup(
    name="daman",
    author="Sofiane Mahiou",
    author_email="mahiou.sofiane@gmail.com",
    description=(
        "A simple package that allows for the direct use of data"
        " stored and managed on a cloud storage service"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sofiane87/daman",
    python_requires=">=3.6.0",
    version="0.2.0",
    packages=find_packages("."),
    package_dir={"": "."},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "dm_configure = daman.commands:configure_command",
            "dm_aws = daman.commands:configure_aws_command",
            "dm_pull = daman.commands:download_command",
            "dm_delete = daman.commands:delete_command",
            "dm_clear = daman.commands:clear_command",
            "dm_summary = daman.commands:summary_command",
        ]
    },
    project_urls={"Bug Tracker": "https://github.com/sofiane87/daman/issues"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
)
