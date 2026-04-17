.data
 secret: .word -357
 msg: .asciiz "Please type a number: "
 toolow: .asciiz "Too low, try again!\n"
 toohigh: .asciiz "Too high, try again!\n"
 hurray: .asciiz "Nice guess! "
 # note: the above should all fit in data memory below address 0x100
.text
 main:
 
 #set up some variables
 lui $8, 0x8000 # a = 0x80000000 // used for memory-mapped I/O
 addiu $2, $0, 0x0	# store value 0 in r2 (r2 store our number)
 addiu $10, $0, 0x0a	# store ascii code for new line in r10
 addiu $11, $0, 0x2d	# store ascii code for hyphen-minus in r11
 addiu $5, $0, 0x0a	# store value 10 in r5
 addiu $6, $0, 0x0	# store value 10 in r6 (0 = postive, 1 = negative)
 addiu $7, $0, 0x30	# store value 0x30 in r7 (for convert character to number)
 #instruction
 la $4, msg	# put address of message into argument register
 jal printString	# call printString("Please type a number: ")
 nop
 addiu $4, $0, 0x100 # use location 0x100 for argument 
 jal readString # call readString(0x100)
 nop
 addiu $4, $0, 0x100 # use location 0x100 for argument
 
 jal atoi # call atoi(0x100)
 nop
 la $3, secret
 lw $3, 0($3)
 sub $3, $2, $3
 beq $3, $0, justright
 bgtz $3, over
 under:
 la $4, toolow
 jal printString
 nop
 j main
 over:
 la $4, toohigh
 jal printString
 nop
 j main
 justright:
 la $4, hurray
 jal printString
 nop
 endlessLoop:
 j endlessLoop

 
printString:

printStringLoop:
lb $9, 0x0($4)	# load character at address store in r4
blez $9, stopPrint	# call stopPrint if r9 <= 0 (character is '0')
sb $9, 0x8($8)	# store character in special address (0x80000008) to write on console
addiu $4, $4, 0x1 # advance r4 to the next memory location
j printStringLoop # loop back to the printStringLoop

stopPrint:
jr $31	# return

readString:

readKbdStatusLoop: # do {
 lb $9, 0($8) # c = load from keyboard status register
 beq $0, $9, readKbdStatusLoop # } while (kbd status c was zero)
 lb $9, 4($8) # c = load from keyboard data register
 sb $9, 0x8($8)	# store character in special address (0x80000008) to write on console
 beq $9, $10, stopReading # if (c == newline) go to stopReading
 beq $9, $11, negativeSign	# if (c == hyphen-minus) go to negativeSign
 sb $9, 0($4) # stores this character into memory
 addiu $4, $4, 1 # p++ // advance pointer to next address
 j readKbdStatusLoop # go back to nearly the top and do it all again
 negativeSign:
 addiu $6, $6, 0x1 # set value in r6 to 1 ( 0 = positive, 1 = negative)
 j readKbdStatusLoop # go back to nearly the top and do it all again
stopReading:
 sb $0, 0($4) # r4 = 0 // store a terminating zero into memory
 jr $31 # return
 
 atoi:
 atoiLoop:
 lb $9, 0($4) # loac character in address store at r4+0x0 to r9
 blez $9, negativeConvert
 sub $9, $9, $7 # convert character to number (subtract the hex code to 0x30)
 mult $2, $5 # r2 store our number, so take that number and multiply with 10
 mflo $2	# move the result to r2
 add $2, $2, $9 # add the current number to the the number we converted
 addiu $4, $4, 0x1 # advance r4 to the next memory location
 j atoiLoop # go back to the loop
 negativeConvert:
 beq $0, $6, stopAtoi
 sub $2, $0, $2
 addiu $6, $0, 0x0	# store value 10 in r6 (0 = postive, 1 = negative)
 stopAtoi:
 jr $31 # return



