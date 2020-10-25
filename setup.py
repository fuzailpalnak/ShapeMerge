from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "shapely == 1.7.0",
    "geojson >= 2.5.0",
    "py-oneliner == 0.0.1"
]

setup(
    name="shape_merge",
    version="1.0.1",
    author="Fuzail Palnak",
    author_email="fuzailpalnak@gmail.com",
    url="https://github.com/fuzailpalnak/ShapeMerge",
    description="Library that Merges Geo Spatial Shapes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='~=3.3',
    install_requires=install_requires,
    keywords=["GIS, Merge, Shapely, Fiona, Polygon, MultiPolygon, Geometry"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
)
