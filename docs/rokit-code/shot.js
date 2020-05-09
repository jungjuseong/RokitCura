var coord = {x:11.0, y:40.5, z:2.0};

function msg() {
  return `D2; X${coord.x} Y${coord.y}
    G01 Z${coord.z - 8}.
    G04 P1000
    M301
    G04 P2000 
    M330
    G04 P500
    G01 Z${coord.z}.
    G01 X${coord.x} Y${coord.y} Z${coord.z} F700
    G01 A0.
    G01 B2.\n`
}

for (i = 0; i < 11; i++) {
   console.log(msg(i));
   coord.y -= 9
}

 coord.x += 63

for (i = 0; i < 11; i++) {
   coord.y += 9
   console.log(msg(i));

}