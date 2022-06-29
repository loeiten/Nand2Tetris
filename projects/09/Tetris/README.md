# Tetris

This is the Jack implementation of [tetris](https://tetris.com) by Alexey Pajitnov.



## Tetris rules

The tetris guideline can be found at

[Tetris guideline](https://tetris.fandom.com/wiki/Tetris_Guideline)

### Included

- [Scroing](https://tetris.fandom.com/wiki/Scoring#Guideline_scoring_system) based on [zone.tetris](https://web.archive.org/web/20070623041317/http://zone.tetris.com/page/manual)
  - With the exception of:
    - T-spin score
    - Combo score
- [Gravity](https://tetris.fandom.com/wiki/Tetris_Worlds#Gravity)
- [7-bag Random Generator](https://tetris.fandom.com/wiki/Random_Generator)
- [Standard Rotation System](https://tetris.fandom.com/wiki/SRS)
- [Wall kicks](https://tetris.fandom.com/wiki/SRS#Wall_Kicks)
- Fixed goal level up (10 lines)
  - With the exception of:
    - T-spin level up

### Excluded

- [T-spin](https://tetris.fandom.com/wiki/T-Spin)
- [Floor kicks](https://tetris.fandom.com/wiki/Floor_kick)
- [Hold piece](https://tetris.fandom.com/wiki/Hold_piece)
- [Logo](https://tetris.wiki/File:The_Tetris_Company_logo.png)

## Design

| File                    | Prupose                                                       | Key methods                                                                  |
|-------------------------|---------------------------------------------------------------|------------------------------------------------------------------------------|
| `Algorithm.jack`        | General purpose algorithms                                    | `mod` - Return the modulus                                                   |
|                         |                                                               | `intInArray` - Check if an integer is in the array                           |
| `Background.jack`       | Background which tetrominos can be drawn on                   | `collapse` - Collapse full rows                                              |
|                         |                                                               | `drawFrame` - Draw the full frame                                            |
|                         |                                                               | `drawMesh` - Draw a mesh on the background                                   |
|                         |                                                               | `drawRows` - Draw specific row in a certain color (used for blinking effect) |
|                         |                                                               | `clearLinesAnimation` - Animate clear lines                                  |
| `LCGRandom.jack`        | Random number generator                                       | `randRange` - Return a random int                                            |
| `Main.jack`             | The main function                                             | `main` - Draws the splash screen, sets the seed and runs the game            |
| `Mesh.jack`             | A mesh where elements have state 0 or 1                       | `getState` - Get the state of an element                                     |
|                         |                                                               | `setState` - Get the state of an element                                     |
|                         |                                                               | `addTetrominoToMesh` - Add a tetromino to the mesh                           |
| `NextTetrominos.jack`   | Generate, return and display the next tetrominos              | `getNextTetromino` - Return the next tetromino                               |
|                         |                                                               | `generateBag` - Generate a 7-bag of tetrominos using                         |
| `Score.jack`            | Update and display the score (including line and level count) | `updateScore` - Update the score                                             |
|                         |                                                               | `updateLine` - Update the line count                                         |
|                         |                                                               | `updateLevel` - Update the level                                             |
| `SplashScreen.jack`     | Display splash screen and set random number seed              | `printSplashScreen` - Print the splash screen and return the seed            |
| `Statistics.jack`       | Update and display the statistics                             | `updateCounter` - Update the count of a specific tetromino                   |
| `TetrisGame.jack`       | Updaate the model of the game                                 | `run` - Run the game until game over                                         |
|                         |                                                               | `tetrominoFall` - Let the tetromino fall and move                            |
|                         |                                                               | `removeFullLines` - Remove any lines needing removaljk                       |
|                         |                                                               | `updateGameSpeed` - Update the game speed                                    |
| `Tetromino.jack`        | Manipulate individual tetrominos                              | `moveDown` - Move the tetromino down                                         |
|                         |                                                               | `moveLeft` - Move the tetromino down                                         |
|                         |                                                               | `moveRight` - Move the tetromino down                                        |
|                         |                                                               | `rotate` - Rotate the tetromino clockwise with wall kick (if applicable)     |
| `TetrominoSpawner.jack` | Spawn individual tetrominos                                   | `spawn{I,J,L,O,S,T,Z}` - Spawn a tetromino                                   |

## Implementation details

### Wall kick data

Translated from [wall kicks](https://tetris.fandom.com/wiki/SRS#Wall_Kicks), on the form `(y-index, x-index)`

#### For the I teromino

| Rotaion state from >> Rotation state to | Test 2  | Test 3  | Test 4   | Test 5   |
|-----------------------------------------|---------|---------|----------|----------|
| 0>>1                                    | (0, -2) |  (0, 1) | (-1, -2) |  ( 2, 1) |
| 1>>2                                    | (0, -1) | (0, 2)  | ( 2, -1) | (-1, 2)  |
| 2>>3                                    | (0, 2)  | (0, -1) | ( 1, 2)  | (-2, -1) |
| 3>>0                                    | (0, 1)  | (0, -2) | (-2, 1)  | ( 1, -2) |


#### For the J, L, T, S, Z terominos

| Rotaion state from >> Rotation state to | Test 2  | Test 3   | Test 4    | Test 5   |
|-----------------------------------------|---------|----------|-----------|----------|
| 0>>1                                    | (0, -1) | ( 1, -1) | (-2, 0, ) | (-2, -1) |
| 1>>2                                    | (0, 1)  | (-1, 1)  | ( 2, 0, ) | ( 2, 1)  |
| 2>>3                                    | (0, 1)  | ( 1, 1)  | (-2, 0, ) | (-2, 1)  |
| 3>>0                                    | (0, -1) | (-1, -1) | ( 2, 0, ) | ( 2, -1) |

### Frame calculations

(0-I, 1-J, 2-L, 3-O, 4-S, 5-T, 6-Z)

Text: 23 rows of 64 characters
Screen: 256 rows of 512 pixels

### Calculation of frame size

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

We need 4*6 = 24 elements

The max is obtained when the left-over pixels are less than the size of a block

```text
256 - 5 - 24*(size + 1) > size
251 - 24*size - 24 *1 > size
227 > size + 24*size
227 > 25*size
227/25 > size
9 > size
```

So max size is 8

All 24 blocks will therefore occupy

```text
[Num blocks] * (size + spacing + [1 for the start position of next block])
24*(8 + 1 + 1) = 240
```

If we pad equally top and bottom, we get

```text
256-240 = 16
16 - bottom line - top line =
16 - 2 = 14
14/2 = 7
```

Thus, we get `frameStartY = 6`

## Helpful resources

- Notes about memory management: [Ray tracer](https://blog.alexqua.ch/posts/from-nand-to-raytracer/) with [source code](https://github.com/aquach/from-nand-to-raytracer)

### Random number generator

- [Linear Congruential Generator](https://web.archive.org/web/20201022060109/http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/Pseudo-Random-Number-Generator-td4026059.html), **NOTE**: The bug in `randRange` (addressed by Mark in some posts below)
- [LFSR32Rand](https://web.archive.org/web/20200126223144/http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/LFSR32Rand-A-new-Random-Number-Generator-for-Jack-td4029928.html)
- [Coursea thread 1](https://www.coursera.org/learn/nand2tetris2/discussions/forums/I-Q0YCj3EeaZ8Apto8QB_w/threads/JsMZ_mRTTEmDGf5kU5xJHQ)
- [Coursera thread 2](https://www.coursera.org/learn/nand2tetris2/discussions/forums/I-Q0YCj3EeaZ8Apto8QB_w/threads/LiyUrABwEee0IhLPmsG3Vg)
