main:
addiu $4, $0, 0x30 # argument is memory location 0x30
jal readString # jumps to your printString code
nop
nop

endlessloop:
j endlessloop # if user typed 4 letter word, then loop forever endlessly

readString:
 addiu $2, $0, 0 # n = 0 // this is our counter
 lui $8, 0x8000 # a = 0x80000000 // used for memory-mapped I/O
 addiu $10, $0, 0x0a # temp_1 = ascii newline
 addiu $11, $0, 0x20 # temp_2 = ascii space
readKbdStatusLoop: # do {
 lb $9, 0($8) # c = load from keyboard status register
 beq $0, $9, readKbdStatusLoop # } while (kbd status c was zero)
 lb $9, 4($8) # c = load from keyboard data register
 beq $9, $10, stopReading # if (c == newline) go to stopReading
 beq $9, $11, stopReading # if (c == space) go to stopReading
 sb $9, 0($4) # stores this character into memory
 sb $9, 0x8($8)	# store character in special address (0x80000008) to write on console
 addiu $4, $4, 1 # p++ // advance pointer to next address
 addiu $2, $2, 1 # n++
 j readKbdStatusLoop # go back to nearly the top and do it all again
stopReading:
 sb $0, 0($4) # r4 = 0 // store a terminating zero into memory
 jr $31 # retur