from setuptools import setup, find_packages

setup(
    name="daman",
    python_requires=">=3.6.0",
    version="0.1",
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
        ]
    },
)
