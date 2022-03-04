from platform import python_version
from setuptools import setup


setup(
    name="sprut",
    version="0.0.1",
    description="Securely and simply transfer files \
                from one computer to another 📦",
    author="Illya Mosiychuk",
    author_email="illya08mosiychuk@gmail.com",
    license="MIT",
    url="https://github.com/qXytreXp/sprut",
    packages=["sprut"],
    package_dir={"sprut": "sprut/"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Enviroment :: Console",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=["cryptography==36.0.1", "requests==2.27.1"],
    entry_points={
        "console_scripts": [
            "sprut=sprut",
        ]
    },
)
