.data
 msg: .asciiz "Please type a number: "

.text
main:
initial:
# initial variables
lui $8, 0x8000	# special character
addiu $3, $0, 0x0	# store value 0 in r3 (this 10 bit data in r2 control the led signal)
addiu $6, $0, 0x0a	# store value 10 in r6
addiu $7, $0, 0x30	# store value 0x30 in r7
addiu $10, $0, 0x0a	# store ascii code for new line in r10
instruction:
# instruction
 addiu $2, $0, 0x0	# store value 0 in r2 (current input)
 addiu $5, $0, 0x1	# store value 1 in r5 (this 10 bit data represent the user led control signal)
 la $4, msg	# put address of message into argument register
 jal printString	# call printString("Please type a number: ")
 nop
 addiu $4, $0, 0x100 # use location 0x100 for argument 
 jal readString # call readString(0x100)
 nop
 addiu $4, $0, 0x100 #use location 0x100 for argument
 jal atoi
 nop
 addiu $4, $0, 0x100 #use location 0x100 for argument
 jal ledControl
 nop
 j instruction
 
readString:
readKbdStatusLoop: # do {
 lb $9, 0($8) # c = load from keyboard status register
 beq $0, $9, readKbdStatusLoop # } while (kbd status c was zero)
 lb $9, 4($8) # c = load from keyboard data register
 sb $9, 0x8($8)	# store character in special address (0x80000008) to write on console
 beq $9, $10, stopReading # if (c == newline) go to stopReading
 sb $9, 0($4) # stores this character into memory
 addiu $4, $4, 1 # p++ // advance pointer to next address
 j readKbdStatusLoop # go back to nearly the top and do it all again
stopReading:
 sb $0, 0($4) # r4 = 0 // store a terminating zero into memory
 jr $31 # return

printString:
printStringLoop:
lb $9, 0x0($4)	# load character at address store in r4
blez $9, stopPrint	# call stopPrint if r9 <= 0 (character is '0')
sb $9, 0x8($8)	# store character in special address (0x80000008) to write on console
addiu $4, $4, 0x1 # advance r4 to the next memory location
j printStringLoop # loop back to the printStringLoop
stopPrint:
jr $31	# return

 atoi:
 atoiLoop:
 lb $9, 0($4) # load character in address store at r4+0x0 to r9
 blez $9, stopAtoi
 sub $9, $9, $7 # convert character to number (subtract the hex code to 0x30)
 mult $2, $6 # r2 store our number, so take that number and multiply with 10
 mflo $2	# move the result to r2
 add $2, $2, $9 # add the current number to the the number we converted
 addiu $4, $4, 0x1 # advance r4 to the next memory location
 j atoiLoop # go back to the loop
 stopAtoi:
 jr $31 # return

ledControl:
 sllv $5, $5, $2 # shift the value in r5 [r2] bits
 xor $3, $3, $5 # xor the value in r3 with r5 and store back to r3 (toggle the signal of all Led)
 sw $3, 0xc($8)
 jr $31 # return
