from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "shapely == 1.7.0",
    "fiona >= 1.8.13",
    "geojson >= 2.5.0",
    "rtree >= 0.9.4",
]

setup(
    name="shape_merge",
    version="1.0.0",
    author="Fuzail Palnak",
    author_email="fuzailpalnak@gmail.com",
    description="Library that Merges Geo Spatial Shapes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='~=3.3',
    install_requires=install_requires,
    keywords="GIS Merge Shapely Fiona Polygon MultiPolygon",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
