import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name='samsync-toose',
    version="0.8.0",
    author="Christopher DiTusa",
    author_email="cditusa@gmail.com",
    description="sync on-prem resources with Samanage SaaS inventory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toose/samsync",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)