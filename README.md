# UTI-misalignment
Python implementation of 

- Tamás Gábor Csapó, Kele Xu, ,,Quantification of Transducer Misalignment in Ultrasound Tongue Imaging'', submitted to Interspeech 2020.
- Tamás Gábor Csapó, Kele Xu, Andrea Deme, Tekla Etelka Gráczi, Alexandra Markó, ,,Transducer Misalignment in Ultrasound Tongue Imaging'', submitted to Interspeech 2020, Show & Tell.

**Requirements**

- Python 3.6.9
- ultrasuite-tools, https://github.com/UltraSuite/ultrasuite-tools
- ...etc... see requirements.txt

**Supplementary material for the regular paper**

- [all MSE, SSIM, CW-SSIM figures (Ultrasuite dataset)](show_figures_UltraSuite.md)
- [all MSE, SSIM, CW-SSIM figures (Hungarian children dataset)](show_figures_Hungarian_children.md)
- [all MSE, SSIM, CW-SSIM descriptive statistics (Ultrasuite dataset)](show_table_UltraSuite.md)
- [all MSE, SSIM, CW-SSIM descriptive statistics (Hungarian children dataset)](show_table_Hungarian_children.md)

**Tool for the Show & Tell paper**

```
python3 check_MSE_tool.py

This is a command line tool for checking
Transducer Misalignment in Ultrasound Tongue Imaging,
   and can be used with raw ultrasound scanline data
   (e.g. 'Micro' system of Articulate Instruments Ltd.)
Need 1 argument:
   please provide a directory containing the raw .ULT files
```