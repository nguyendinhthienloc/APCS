.data
secret:  .word -357
msg:     .asciz "Please type a number: "
toolow:  .asciz "Too low, try again!\n"
toohigh: .asciz "Too high, try again!\n"
hurray:  .asciz "Nice guess! "

.text
main:
    # Print prompt
    la $4, msg
    jal printString
    
    # Read string into 0x100
    li $4, 0x100
    jal readString
    
    # Convert string to int
    li $4, 0x100
    jal atoi
    
    # Check guess
    la $3, secret
    lw $3, 0($3)
    sub $3, $2, $3     # diff = guess - secret
    beq $3, $0, justright
    bltz $3, under

over:
    la $4, toohigh
    jal printString
    j main

under:
    la $4, toolow
    jal printString
    j main

justright:
    la $4, hurray
    jal printString
infiniteloop:
    j infiniteloop

# --- Helper Functions ---

# atoi: Converts string at $4 to integer in $2
atoi:
    li $2, 0            # result = 0
    li $12, 1           # sign = 1
    lb $9, 0($4)        # load first char
    li $10, 45          # ASCII '-'
    bne $9, $10, atoi_loop
    li $12, -1          # sign = -1
    addiu $4, $4, 1     # p++
atoi_loop:
    lb $9, 0($4)
    beq $9, $0, atoi_done
    li $10, 10          # newline
    beq $9, $10, atoi_done
    li $10, 32          # space
    beq $9, $10, atoi_done
    
    addiu $9, $9, -48   # c - '0'
    # result = result * 10
    sll $10, $2, 3      # result * 8
    sll $11, $2, 1      # result * 2
    add $2, $10, $11
    add $2, $2, $9      # + digit
    
    addiu $4, $4, 1     # p++
    j atoi_loop
atoi_done:
    li $10, 1
    beq $12, $10, atoi_end
    sub $2, $0, $2      # apply negative sign
atoi_end:
    jr $31

# readString: reads until space or newline, echoes to console
readString:
    addiu $2, $0, 0     # count = 0
    lui $8, 0x8000      # MMIO base
    ori $11, $8, 0x0008 # Console address
readString_loop:
    lb $9, 0($8)        # Kbd status
    beq $0, $9, readString_loop
    lb $9, 4($8)        # Kbd data
    
    li $10, 10          # newline
    beq $9, $10, readString_stop
    li $10, 32          # space
    beq $9, $10, readString_stop
    
    sb $9, 0($11)       # Echo to console
    sb $9, 0($4)        # Store in memory
    addiu $4, $4, 1
    addiu $2, $2, 1
    j readString_loop
readString_stop:
    sb $0, 0($4)        # null terminator
    jr $31

# printString: Prints null-terminated string at $4
printString:
    lui $8, 0x8000
    ori $8, $8, 0x0008  # Console output
printString_loop:
    lb $9, 0($4)
    beq $9, $0, printString_done
    sb $9, 0($8)
    addiu $4, $4, 1
    j printString_loop
printString_done:
    jr $31