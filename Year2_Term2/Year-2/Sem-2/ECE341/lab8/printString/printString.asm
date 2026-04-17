main:
addiu $4, $0, 0x30 # argument is memory location 0x30
jal readWithoutEcho # jumps to the readWithoutEcho code
nop # ignore return value in r2, we don't need it
nop
addiu $4, $0, 0x30 # argument is memory location 0x30
jal printString # jumps to your printString code
nop
nop
addiu $3, $0, 4 # put constant 4 into register
bne $2, $3, main # go back and do it again if string wasn't 4 letters long
endlessloop:
j endlessloop # if user typed 4 letter word, then loop forever endlessly

readWithoutEcho:
 addiu $2, $0, 0 # n = 0 // this is our counter
 lui $8, 0x8000 # a = 0x80000000 // used for memory-mapped I/O
readKbdStatusLoop: # do {
 lb $9, 0($8) # c = load from keyboard status register
 beq $0, $9, readKbdStatusLoop # } while (kbd status c was zero)
 lb $9, 4($8) # c = load from keyboard data register
 addiu $10, $0, 0x0a # temp = ascii newline
 beq $9, $10, stopReading # if (c == newline) go to stopReading
 sb $9, 0($4) # *p = c // stores this character into memory
 addiu $4, $4, 1 # p++ // advance pointer to next address
 addiu $2, $2, 1 # n++
 j readKbdStatusLoop # go back to nearly the top and do it all again
stopReading:
 sb $0, 0($4) # *p = 0 // store a terminating zero into memory
 jr $31 # return
 
printString:
addiu $2, $0, 0x0 #initialize r2 = 0 (counter)

printStringLoop:
lb $9, 0x0($4)	# load character at address store in r4
blez $9, stopPrint	# call stopPrint if r9 <= 0 (character is '0')
sb $9, 0x8($8)	# store character in special address (0x80000008) to write on console
addiu $4, $4, 0x1 # advance r4 to the next memory location
addiu $2, $2, 0x1 # counter increment
j printStringLoop # loop back to the printStringLoop

stopPrint:
jr $31	# return
