# Silk Icon Scalable

![cc-by-sa 3.0](https://licensebuttons.net/l/by-sa/3.0/88x31.png)

The classic silk icon set recreated (& extended) as SVG

## [Preview, and comparison with the original](https://frhun.de/silk-icon-scalable/preview/)


## Generating from sources:

Inkscape and Pyhton 3 are assumed to be installed,
and present in the `$PATH`.
Generating the combined icons in ./generate:

```sh
# Install svgutils
pip install svgutils

# Install svgo
# Via npm
npm -g install svgo
# -- OR--
# Via yarn
yarn global add svgo

# generate the overlay variants in ./generate
python combine

# generate the preview page
python preview/genindex.py

```