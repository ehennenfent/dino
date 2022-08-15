from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="dino",
    version="0.1.0",
    description="Openscale dino game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ehennenfent/dino",
    author="Eric Hennenfent",
    author_email="eric@hennenfent.com",
    package_dir={"": "dino"},
    packages=find_packages(where="src"),
    python_requires=">=3.9, <4",
    install_requires=["matplotlib", "numpy", "pyserial"],
    entry_points={
        "console_scripts": [
            "scaleplot=dino.__main__:main",
            "scaleread=dino.openscale_serial.__main__:main",
        ],
    },
)
