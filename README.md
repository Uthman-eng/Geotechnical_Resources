# Geotechnical Resources

A growing collection of Python tools and reference notes for ground engineering.

## Purpose

Desk studies and ground investigation (GI) involve a lot of repetitive work: typing coordinates into CAD, scrolling through AGS files, and downloading borehole logs one at a time. I have created some scripts, and i will use this repo as a collections of small scripts and resources i found to be helpful.

The aim is for these to be used as a resource and templates.

You don't need to be a programmer, however basic knowledge on python and the terminal is helpful. Each script has a **"SETTINGS block"** at the top to explain the code, and change the values marked `# <--` and run it to your project needs.

## What I've mainly used it for

| Task | Tool |
|---|---|
| Plotting Google Earth (KML) points into AutoCAD | [AutoCAD plotting](tools/autocad-plotting/README.md) |
| Plotting a list of coordinates (BH/TP locations) into AutoCAD | [AutoCAD plotting](tools/autocad-plotting/README.md) |
| Quick look at AGS data: which groups exist and what's in them | [AGS analysis](tools/ags-analysis/README.md) |
| Getting every BGS borehole log in a site area as one PDF | [BGS data](tools/bgs-data/README.md) |

## Repo layout

```
Geotechnical_Resources/
├── README.md            <- you are here
├── LICENSE
├── requirements.txt     <- Python libraries to install
├── docs/                <- reference notes
├── tools/               <- my scripts + simple tools (lightly checked)
│   └── <tool-name>/
│       ├── README.md
│       ├── *.py         <- python scripts
│       └── examples/    <- sample data and notebooks
└── unchecked/           <- mostly AI-written, NOT yet reviewed
    └── <tool-name>/     <- same layout as tools/
```

## Contents

**Tools**
- [AutoCAD plotting](tools/autocad-plotting/README.md): KML or CSV coordinates -> AutoCAD
- [AGS analysis](tools/ags-analysis/README.md): AGS4 file -> groups and a preview of the key data
- [BGS data](tools/bgs-data/README.md): site area -> BGS borehole list and logs as PDF

**Unchecked** ([what this means](unchecked/README.md))
- [AGS detailed analysis](unchecked/ags-analysis/README.md): strata summary, SPT by stratum, N vs depth plot, Excel

**Reference notes**
- [Python resources](docs/python-resources.md): useful libraries, with short examples
- [BGS API guide](docs/bgs-api.md): how to get BGS data for any area

## Getting started

1. Install [Python](https://www.python.org/downloads/) 3.9 or newer
2. Download this repo.
3. Install the libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Open a tool folder, read its README, edit the SETTINGS block and run the script **from inside that folder**:
   ```bash
   cd tools/bgs-data
   python bgs_borehole_search.py
   ```

## Plans

This repo will grow over time. Planned areas:
- More tools for routine desk study and GI tasks
- More AGS analysis, e.g. lab test results
- More reference notes on useful libraries and data sources

## AI-assisted code

Some code in this repo was written or restructured with AI (Claude):
- **[`tools/`](tools/)**: my own scripts, plus simple tools tidied or written with AI. Lightly checked: tested on the example data, not fully reviewed.
- **[`unchecked/`](unchecked/README.md)**: larger additions mostly written by AI and **not yet reviewed**. They move to `tools/` once they've been checked.

Each tool README has a **Review status** table showing who wrote each file and whether it has been reviewed.

## Disclaimer

These tools are provided 'as-is' and are not checked or certified software. **Always check the outputs** against the original data. Third-party data (e.g. BGS) remains subject to its owner's terms.

## Licence

[MIT](LICENSE)
