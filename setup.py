from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="EmailSenderPy",  
    version="0.0.11",  
    description="A Python package for sending emails to users from a MongoDB database",
    long_description=open("./README.MD").read(),  
    long_description_content_type="text/markdown", 
    author="H3LL0U",
    url="https://github.com/H3LL0U/https://github.com/H3LL0U/EmailPy",  
    packages=find_packages(),  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    zip_safe=False,
    install_requires=parse_requirements('./requirements.txt')  # Read dependencies
)
