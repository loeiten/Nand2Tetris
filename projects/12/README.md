# Implementing OS

As my implementation of screen goes horribly slow (even after applying the [tips by Mark Armbrust]()), I decided to reverse engineer the `Screen.drawHorizontal` from the `Screen.vm` file in `tools/OS`.

This is how the function looks:

```text
function void drawHorizontal(var int argument0, var int argument1, var int argument2){
  var int local0;
  var int local1;
  var int local2;
  var int local3;
  var int local4;
  var int local5;
  var int local6;
  var int local7;
  var int local8;
  var int local9;
  var int local10;

  let local7 = Math.min(argument1, argument2);
  let local8 = Math.max(argument1, argument2);

  if((argument0 > (-1)) & (argument0 < 256) & (local7 < 512) & (local8 > (-1))){
    line 533
  } else{

  }
}
```
