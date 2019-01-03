from setuptools import setup

setup(
    name='itree',
    version='0.0.1',
    url='',
    license='MIT',
    author='Bob Zimmermann',
    author_email='robert.zimmermann@univie.ac.at',
    description='An interval tree data structure',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        " Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    packages=["itree"],
    test_require=["pytest"]
)


