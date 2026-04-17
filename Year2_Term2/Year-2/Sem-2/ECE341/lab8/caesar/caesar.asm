.data
 message_for_number: .asciiz "Please type a number: "
 message_for_secret_sentence: .asciiz "Please type a secret sentence: "
 message_for_encoded_sentence: .asciiz "\nEncoded message is: "
 
.text
main:
initialize:
addiu $5, $0, 0x0a	# store value 10 in r5
addiu $7, $0, 0x30	# store value 0x30 in r7 (for convert character to number)
lui $8, 0x8000 # a = 0x80000000 // used for memory-mapped I/O
addiu $10, $0, 0x0a	# store ascii code for new line in r10
addiu $11, $0, 0x2d	# store ascii code for hyphen-minus in r11
addiu $12, $0, 0x1a	# store value 26
addiu $13, $0, 0x41	# store ascii code for upper case A
addiu $14, $0, 0x5a	# store ascii code for upper case Z
addiu $15, $0, 0x61	# store ascii code for lower case a
addiu $16, $0, 0x7a	# store ascii code for lower case z
instruction:
addiu $2, $0, 0x0 # reset r2 to 0 (number)
addiu $6, $0, 0x0	# store value 10 in r6 (0 = postive, 1 = negative)
la $4, message_for_number	# put address of message_for_number into argument register
jal printString
nop
addiu $4, $0, 0x100	# set location 0x100 for argument
jal readString
nop
addiu $4, $0, 0x100 # use location 0x100 for argument
jal atoi
nop
la $4, message_for_secret_sentence # put address of message_for_secret_sentence into argument register
jal printString
nop
addiu $4, $0, 0x200 # set location 0x200 for argument
jal readWithoutEcho
nop
addiu $3, $0, 0x300 # set location 0x300 for argument
addiu $4, $0, 0x200 # set location 0x200 for argument
jal caesarCipher
nop
addiu $3, $0, 0x300 # set location 0x300 for argument
la $4, message_for_encoded_sentence # put address of message_for_encoded_sentence into argument register
jal printString
nop
addiu $4, $0, 0x300 # set location 0x300 for argument
jal printString
j instruction

readString:
readStatusLoop: # do {
 lb $9, 0($8) # c = load from keyboard status register
 beq $0, $9, readStatusLoop # } while (kbd status c was zero)
 lb $9, 4($8) # c = load from keyboard data register
 sb $9, 0x8($8)	# store character in special address (0x80000008) to write on console
 beq $9, $10, stopReading # if (c == newline) go to stopReading
 beq $9, $11, negativeSign	# if (c == hyphen-minus) go to negativeSign
 sb $9, 0($4) # stores this character into memory
 addiu $4, $4, 1 # p++ // advance pointer to next address
 j readStatusLoop # go back to nearly the top and do it all again
 negativeSign:
 addiu $6, $6, 0x1 # set value in r6 to 1 ( 0 = positive, 1 = negative)
 j readStatusLoop # go back to nearly the top and do it all again
 
readWithoutEcho:
readKbdStatusLoop: # do {
 lb $9, 0($8) # c = load from keyboard status register
 beq $0, $9, readKbdStatusLoop # } while (kbd status c was zero)
 lb $9, 4($8) # c = load from keyboard data register
 beq $9, $10, stopReading # if (c == newline) go to stopReading
 sb $9, 0($4) # *p = c // stores this character into memory
 addiu $4, $4, 1 # p++ // advance pointer to next address
 j readKbdStatusLoop # go back to nearly the top and do it all again
stopReading:
 sb $0, 0($4) # *p = 0 // store a terminating zero into memory
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
 stopAtoi:
 jr $31 # return
 
caesarCipher:
addiu $17, $0, 0x0 # bool variable to check whether character in range [A,Z] or [a,z]
addiu $19, $0, 0x0 # bool variable to check whether character is upper case or lowercase
lb $9, 0x0($4)	# load character in original message
blez $9, stopCaesarCipher	# call stopCaesarCipher if r9 <= 0 (character is '0')
j checkCharacterInRange
afterCheckCharacterInrage:
lb $18, 0x0($4) # temp character
bgtz $17, process
j checkLower
afterCheckLower:
bgtz $19, lowerCase
add $20, $0, $13
j continue
lowerCase:
add $20, $0, $15
continue:
lb $18, 0x0($4) # temp character
add $21, $0, $2 #temp r2
beq $0, $6, continueProcess
sub $21, $0, $2 # abs([r2])
continueProcess:
add $18, $18, $21 # hex code character + shift
sub $18, $18, $20 # [r18]-[r20]
div $18, $12	# [r18]%26 to get the remainder
mflo $18	# load remainder in lo to r18
beq $0, $6, handleNegative
sub $18, $12, $18
handleNegative:
add $18, $18, $20 #[r18]+[r20]
process:
sb $18, 0($3) # store encoded character
addiu $3, $3, 0x1 # advance pointer r3
addiu $4, $4, 0x1 # advance pointer r4
j caesarCipher
stopCaesarCipher:
jr $31 # return

checkCharacterInRange:
lb $18, 0x0($4) # temp character
sub $18, $18, $13
bltz $18, outRange
lb $18, 0x0($4) # temp character
sub $18, $16, $18
bltz $18, outRange
lb $18, 0x0($4) # temp character
sub $18, $14, $18
bltz $18, nextCondition
j stopCheckCharacterInRange
nextCondition:
lb $18, 0x0($4) # temp character
sub $18, $18, $15
bltz $18, outRange
j stopCheckCharacterInRange
outRange:
addiu $17, $0, 0x1
stopCheckCharacterInRange:
j afterCheckCharacterInrage

checkLower:
lb $18, 0x0($4) # temp character
sub $18, $18, $16
blez $18, lower
j stopCheckLower
lower:
addiu $19, $0, 0x1
stopCheckLower:
j afterCheckLower
