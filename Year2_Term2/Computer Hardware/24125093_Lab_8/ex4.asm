.data
prompt: .asciz "Enter LED to toggle (0-9): "

.text
main:
    la $4, prompt
    jal printString
    li $4, 0x100
    jal readString
    li $4, 0x100
    jal atoi
    move $4, $2
    jal led
    j main

led:
    lui $8, 0x8000
    ori $8, $8, 0x000C  
    lw $9, 0($8)        
    li $10, 1
    sllv $10, $10, $4   
    xor $9, $9, $10     
    sw $9, 0($8)        
    jr $31

atoi:
    li $2, 0            
    li $12, 1           
    lb $9, 0($4)        
    li $10, 45          
    bne $9, $10, atoi_loop
    li $12, -1          
    addiu $4, $4, 1     
atoi_loop:
    lb $9, 0($4)
    beq $9, $0, atoi_done
    li $10, 10          
    beq $9, $10, atoi_done
    li $10, 32          
    beq $9, $10, atoi_done
    addiu $9, $9, -48   
    sll $10, $2, 3      
    sll $11, $2, 1      
    add $2, $10, $11
    add $2, $2, $9      
    addiu $4, $4, 1     
    j atoi_loop
atoi_done:
    li $10, 1
    beq $12, $10, atoi_end
    sub $2, $0, $2      
atoi_end:
    jr $31

readString:
    addiu $2, $0, 0     
    lui $8, 0x8000      
    ori $11, $8, 0x0008 
readString_loop:
    lb $9, 0($8)        
    beq $0, $9, readString_loop
    lb $9, 4($8)        
    li $10, 10          
    beq $9, $10, readString_stop
    li $10, 32          
    beq $9, $10, readString_stop
    sb $9, 0($11)       
    sb $9, 0($4)        
    addiu $4, $4, 1
    addiu $2, $2, 1
    j readString_loop
readString_stop:
    sb $0, 0($4)        
    jr $31

printString:
    lui $8, 0x8000
    ori $8, $8, 0x0008  
printString_loop:
    lb $9, 0($4)
    beq $9, $0, printString_done
    sb $9, 0($8)
    addiu $4, $4, 1
    j printString_loop
printString_done:
    jr $31
