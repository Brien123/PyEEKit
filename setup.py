import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyEEKit",
    version="0.1.0",
    author="Zeh Brien",
    author_email="zehbrien@gmail.com",
    description="A Python-based software for simulating electronics circuits via code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Brien123/PyEEKit.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "exceptiongroup==1.3.0",
        "exceptiongroup==1.3.0",
        "iniconfig==2.1.0",
        "packaging==25.0",
        "pluggy==1.6.0",
        "Pygments==2.19.2",
        "pytest==8.4.1",
        "tomli==2.2.1",
        "typing_extensions==4.15.0"
    ],
)