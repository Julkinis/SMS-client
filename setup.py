from setuptools import setup

setup(
    name="sms_client",
    version="0.1.0",
    packages=["sms_client"],
    entry_points={
        "console_scripts": [
            "sms-client=sms_client.cli:main",
        ],
    },
)