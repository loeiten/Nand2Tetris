# Tetris

Text: 23 rows of 64 characters
Screen: 256 rows of 512 pixels

## Calculation of frame size

### Play field

Play field = 10x20

Largest block set by vertical/20
Min bottom separation = 1
Bottom line = 1
Min top separation = 1
Top line = 1
Top separation line and block = 1

Total = 5
Each block will occupy: Blocksize + 1 (assume that +1 is for bottom)

The max is obtained when the left-over pixels are less than the size of a block

```text
256 - 5 - 20*(size + 1) > size
251 - 20*size - 20 *1 > size
231 > size + 20*size
231 > 21*size
231/21 > size
11 > size
```

So max size is 10

All 20 blocks will therefore occupy

```text
[Num blocks] * (size + spacing + [1 for the start position of next block])
20*(10 + 1 + 1) = 240
```

If we pad equally top and bottom, we get

```text
256-240 = 16
16 - bottom line - top line =
16 - 2 = 14
14/2 = 7
```

Thus, we get `frameStartY = 6`

#### X in the middle

Don't think the below is too useful

Center of background is
512/2 = 256
Half width of background
122/2 = 61
StartX will therefore be
256 - 61 = 195

---

Have 23 lines, now used 2 => 21 lines

...one line per tetromino

Can draw and find that statistics need

Assume 22 pixels gone to text, what is max tetromino size?

The number 21 comes from stacking tetrominos in a mesh with one width spacing

```text
256 - 22 - 5 - 21*(size + 1) > size
229 - 21*size - 21 *1 > size
208 > size + 21*size
208 > 22*size
208/22 > size
9.45... > size
```

So tetrominos of size 9 should be ok

All 21 blocks will therefore occupy

```text
[Num blocks] * (size + spacing + [1 for the start position of next block])
21*(9 + 1 + 1) = 231
```

If we pad equally top and bottom, we get

```text
256-22-231 = 3
3 - bottom line - top line =
3 - 2 = 1
1/2 = 0
```

No padding

Side: 6*(9+1+1)=66

Characters:
512/64 = 8... so 8 pixel/char i x dir
8*3 = 24
2 character spacing => 24 + 2*8 = 40 pixel extra in frameStartLenX_

```text
[Num blocks] * (size + spacing + [1 for the start position of next block])
19*(9 + 1 + 1) = 209
```


### Next frame

Idea:
Could actually make a class for just drawing tetrominos where input is center pixel...or make it part of tetromino class :)

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

## Design

### Main

Starts the app, initializes the game and launches it

| **Routine** | **Arguments** | **Returns** | **Function** |
|-------------|---------------|-------------|--------------|
|             |               |             |              |

### TetrisGame

- Captures the user's input
- Moves the tetrominos

| **Routine** | **Arguments** | **Returns** | **Function** |
|-------------|---------------|-------------|--------------|
|             |               |             |              |

### TetrominoX

- Deals with the manipulation of the Tetrominos
- Deals with Tetrominos coordinate

| **Routine** | **Arguments** | **Returns** | **Function** |
|-------------|---------------|-------------|--------------|
|             |               |             |              |

### Grid

- Deals with the game grid
- Remove lines when needed

| **Routine** | **Arguments** | **Returns** | **Function** |
|-------------|---------------|-------------|--------------|
|             |               |             |              |

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

## Helpful resources

- Notes about memory management: [Ray tracer](https://blog.alexqua.ch/posts/from-nand-to-raytracer/) with [source code](https://github.com/aquach/from-nand-to-raytracer)
