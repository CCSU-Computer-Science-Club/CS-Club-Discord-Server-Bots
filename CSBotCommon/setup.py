from setuptools import setup

setup(
    name="CSBotCommon",
    version="0.1.0",
    description="Common module for handling the CS Club bots",
    url="https://github.com/CCSU-Computer-Science-Club/CS-Club-Discord-Server-Bots",
    author="CCSU CS Club",
    author_email="",
    license="",
    packages=["CSBotCommon"],
    install_requires=[
        "discord.py>=2.3.2",
        "google-generativeai>=0.2.2",
    ],
    classifiers=[],
)
