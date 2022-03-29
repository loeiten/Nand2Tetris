// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Pseudocode:
// int lhs = R0
// int rhs = R1
// int R2 = 0
// for (int i=0; i<=rhs; ++i){
//     R2 += lhs
// }
// return R2

    @R0  // Set A to the memory address of register 0
    D=M  // Set the data register to the address pointed to by A
    @lhs  // Declare a variable (by pointing A to the first free memory location)
    M=D   // Set this memory location to the value pointed to by the D register

    // Set rhs
    @R1
    D=M
    @rhs
    M=D

    // Set R2 (result) and counter to 0
    @R2
    M=0
    @i
    M=0

(LOOP)  // Declare this line number to be labeled with LOOP
    // Check if the counter is 0
    @rhs
    D=M
    @i
    D=D-M  // rhs-i

    // Jump to STOP if rhs-i=0
    @END
    D;JEQ

    // If condition is not fulfilled: Add lhs to R2
    @lhs
    D=M
    @R2
    D=D+M
    M=D  // Store the result back in memory

    // Increment i
    @i
    M = M+1  // M+1 is its own C-instruction (defined by the ALU chip)

    @LOOP  // Set A to the LOOP line number
    0;JMP  // Jump to the start of the loop

(END)
    @END
    0;JMP  // Jump unconditionally to the line number marked with END
