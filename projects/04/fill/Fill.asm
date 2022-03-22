// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Pseudocode
// bool keyPressed = 0
// for (;;){
//    // Will return 0 (if no key is pressed) or -1 (if a key is pressed)
//    // -1 has the binary value consisting of 16 ones
//    // 0 has the binary value consisting of 16 zeros
//    screenVal = checkIfPressed()
//    setScreenValue(screenVal)
// }
//
// int checkIfPressed(){
//     if(KBD){
//         return -1
//     }
//     else{
//         return 0
//     }
// }
//
// void setScreenValue(int screenVal){
//    // 512*256/16 = 8192 registers to set
//    int lastRow = 8192
//    for (int i=0; i < lastRow; ++i) {
//        int *row =  SCREEN + i
//        *row = screenVal
//    }
// }

    // Initialize keyPressed, screenVal, i and row to 0
    @keyPressed
    M=0
    @screenVal
    M=0
    @i
    M=0
    @row
    M=0

    // Initialize lastRow to 8192
    @8192
    D=A
    @lastRow
    M=D

// START*MAINLOOP**************************************************************
(MAINLOOP)
    // Unconditionally jump to checkIfPressed
    @CHECKIFPRESSED
    0;JMP
(RETURNCHECKIFPRESSED)

    // Set screenVal to keyPressed
    // NOTE: We only do this due to readability
    //       We might as well be using keyPressed
    @keyPressed
    D=M
    @screenVal
    M=D

    // As we have capture the screenVal we unconditionally jump to setScreenValue
    @SETSCREENVALUE
    0;JMP
(RETURNSETSCREENVALUE)

    // Unconditonally jump to the main loop
    @MAINLOOP
    0;JMP
// END*MAINLOOP****************************************************************


// START*CHECKIFPRESSED********************************************************
// NOTE: We probably wouldn't need a function for this as it's a ternary expression
// Check if pressed function
(CHECKIFPRESSED)
    // Check the value of 
    @KBD
    D=M
    @SETKEYPRESSED
    D;JGT // Jump setKeyPressed if keyboard has a non-zero value

    // Else: Set that the key is not pressed
    @keyPressed
    M=0
    // Unconditionally jump to the return of checkIfPressed
    @RETURNCHECKIFPRESSED
    0;JMP

(SETKEYPRESSED)
    @keyPressed
    M=-1
    // Unconditionally jump to the return of checkIfPressed
    @RETURNCHECKIFPRESSED
    0;JMP
// END*CHECKIFPRESSED**********************************************************

// START*SETSCREENVALUE********************************************************
(SETSCREENVALUE)
    // Reset the counter to 0
    @i
    M=0
(SETSCREENVALUELOOP)
    // Check if the condition is reached
    @i
    D=M
    @lastRow
    D=D-M
    // Jump to out of the loop if condition is fulfilled
    // The condition is i < lastRow, so i-lastRow < 0 must be true to continue
    // The first time this is not true is when i-lastRow=0
    @ENDSETSCREENVALUELOOP
    D;JEQ

    // Update row
    @SCREEN
    D=A  // Need the address of this, rather than the memory
    @i
    D=D+M  // This is now the address we would like to manipulate
    @row
    M=D  // Store the value in row (act as pointer)

    @screenVal
    D=M
    @row
    A=M  // Set the address to the address pointed to by the row
    M=D  // Set the value of this address to screenVal

    // Update counter
    @i
    M=M+1

    // Jump unconditionally to the start of the loop
    @SETSCREENVALUELOOP
    0;JMP

(ENDSETSCREENVALUELOOP)
    // Unconditionally jump to the return of setScreenValue
    @RETURNSETSCREENVALUE
    0;JMP
// END*SETSCREENVALUE**********************************************************