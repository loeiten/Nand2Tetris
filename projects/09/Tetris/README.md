# Tetris

Text: 23 rows of 64 characters
Screen: 256 rows of 512 pixels
(256 for half screen)

## Random number generator

- [Linear Congruential Generator](https://web.archive.org/web/20201022060109/http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/Pseudo-Random-Number-Generator-td4026059.html), **NOTE**: The bug in `randRange` (addressed by Mark in some posts below)
- [LFSR32Rand](https://web.archive.org/web/20200126223144/http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/LFSR32Rand-A-new-Random-Number-Generator-for-Jack-td4029928.html)
- [Coursea thread 1](https://www.coursera.org/learn/nand2tetris2/discussions/forums/I-Q0YCj3EeaZ8Apto8QB_w/threads/JsMZ_mRTTEmDGf5kU5xJHQ)
- [Coursera thread 2](https://www.coursera.org/learn/nand2tetris2/discussions/forums/I-Q0YCj3EeaZ8Apto8QB_w/threads/LiyUrABwEee0IhLPmsG3Vg)

## Tetris rules

[Tetris guideline](https://tetris.fandom.com/wiki/Tetris_Guideline)

### Excluded

- [T-spin](https://tetris.fandom.com/wiki/T-Spin)
- [Wall kicks](https://tetris.fandom.com/wiki/SRS#Wall_Kicks)
- [Floor kicks](https://tetris.fandom.com/wiki/Floor_kick)
- [Hold piece](https://tetris.fandom.com/wiki/Hold_piece)
- [Logo](https://tetris.wiki/File:The_Tetris_Company_logo.png) (too much hassle making the bitmap nice)

### Included

- [Scroing](https://tetris.fandom.com/wiki/Scoring#Guideline_scoring_system) based on [zone.tetris](https://web.archive.org/web/20070623041317/http://zone.tetris.com/page/manual)
- [Gravity](https://tetris.fandom.com/wiki/Tetris_Worlds#Gravity)
- [7-bag Random Generator](https://tetris.fandom.com/wiki/Random_Generator)
- [Standard Rotation System](https://tetris.fandom.com/wiki/SRS)


### Delme

Making the sprite for Tetris

```bash
 convert ttcl_orig.png -fuzz 60% -transparent Blue ttcl_tb60.png
 convert ttcl_tb60.png -fuzz 20% -transparent Orange ttcl_tb60_to20.png
 mv ttcl_tb60_to20.png ttcl_tb60_to20_manual_edit.png
 # Manual remove the rest of the background with preview
 convert ttcl_tb60_to20_manual_edit.png -monochrome ttcl_bw.png
 magick ttcl_bw.png -resize 65% ttcl_resize.png
 magick ttcl_resize.png -negate ttcl_resize_invert.png
 magick ttcl_resize_invert.png -monochrome -threshold 10% ttcl_res_inv_mon.png
 # Manual fixes with paint
```
