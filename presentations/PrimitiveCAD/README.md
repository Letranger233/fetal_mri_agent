# PrimitiveCAD 论文精读 PPT (Beamer)

33 slides in Chinese, based on Gao et al., *PrimitiveCAD: An LLM-Based Point-to-CAD Reconstruction with Primitive-Aware Tokenization and Operation Alignment*, ACM MM 2026, arXiv:2610.08698.

## Use in Overleaf
- Download the **entire** `presentations/PrimitiveCAD` folder (including `figures/`), and upload as a ZIP project.
- Select **XeLaTeX** as Compiler, `main.tex` as main document.
- Figures are extracted/cropped from the original paper under CC BY 4.0. The script `prepare_figures.py` can rebuild them from the arXiv PDF when needed: `pip install pymupdf requests && python prepare_figures.py`.
- The paper's Operation Alignment RIoU applied to counts has a normalization ambiguity; the slide deck explicitly flags it.

## Source
https://arxiv.org/abs/2610.08698
