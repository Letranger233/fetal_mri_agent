#!/usr/bin/env python3
"""Download the CC BY 4.0 paper and render figure crops for main.tex.

Usage: python prepare_figures.py
Dependencies: pip install pymupdf requests
"""
from pathlib import Path
import requests
import fitz

URL="https://arxiv.org/pdf/2610.08698"
FIGURES={
    "paper_teaser.png":(0,(47,113,563,270)),
    "pipeline_original.png":(2,(46,75,568,241)),
    "ptv3_pca.png":(3,(45,78,305,270)),
    "primitive_labels.png":(3,(315,76,567,265)),
    "operator_count.png":(4,(42,78,298,278)),
    "feature_lines.png":(4,(314,78,570,279)),
    "qualitative.png":(6,(35,222,577,556)),
    "sft_ablation.png":(7,(38,163,301,362)),
    "rl_ablation.png":(7,(312,162,570,377)),
}
def main():
    target=Path(__file__).parent
    source=target/"paper.pdf"
    if not source.exists():
        response=requests.get(URL,timeout=120,headers={"User-Agent":"PrimitiveCAD-Overleaf/1.0"})
        response.raise_for_status()
        source.write_bytes(response.content)
    doc=fitz.open(source)
    out=target/"figures"
    out.mkdir(exist_ok=True)
    for name,(page,rect) in FIGURES.items():
        pix=doc[page].get_pixmap(matrix=fitz.Matrix(2.5,2.5),clip=fitz.Rect(*rect),alpha=False)
        pix.save(out/name)
        print("Created",out/name)
if __name__=="__main__":main()
