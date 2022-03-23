#!/usr/bin/env python
# coding: utf-8

# In[1]:


from qiskit import *
import math
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
get_ipython().run_line_magic('matplotlib', 'inline')
from qiskit.tools.visualization import plot_histogram
from qiskit.visualization import plot_state_city, plot_bloch_multivector
from qiskit.circuit.library import SXdgGate


# In[ ]:


"S-Transform implementation: 17/02/2022 - Fourth version: Full circuit of the S-Transform"
import pdb

# Initialization
#Signal = "1332313231323132"#1301266621113333" #One dimensional Singal elements 
Signal = "13012666"#211133331301266621113333" #One dimensional Singal elements 

Bit_Precision = 3          #Specify the bit presicion of the singal elements

#Signal length integer
S_lengthi = len(Signal)

#Signal Length (base 2)
S_length = int(math.log(len(Signal),2))

#Position number
P_N = int(math.log(len(Signal)/2,2)) 

#Number of auxiliary qubits  
if P_N >= 2:
    aux_q = P_N - 2

if P_N < 2:
    aux_q = 0


#Odd elements
odd_e = QuantumRegister(Bit_Precision, 'odd') #Generate the registers for the odd elements of the signal

#Even elements
even_e = QuantumRegister(Bit_Precision, 'even') #Generate the registers for the even elements of the signal

#Positions
Number_position = int(P_N + aux_q) #Position number + aux qubits to store the elments

'Note: The number of auxiliary qubits are represented by aux_q'

X_position = QuantumRegister(Number_position, 'x') #Generate the registers for the element's position 


#---Operations---
'Addition variable'
add_q = QuantumRegister(Bit_Precision + 1, 's')

'Rouding variable'
#Odd/even selection
OE = QuantumRegister(1, 'phi')

'Substraction variable'
sub_q = QuantumRegister(Bit_Precision, 'd')

#Classical register
cr = ClassicalRegister(7, 'c') 

#Circuit construction
circuit_ST = QuantumCircuit(odd_e, X_position, even_e, add_q, OE, sub_q, cr)
csxdg_gate = SXdgGate().control() #To generate the V and V*-gates


#Qubits initialization
for ii in range(aux_q, Number_position):
    circuit_ST.h(X_position[ii])


#----------Store the signal values----------
'Block representation of the signal'
circuit_ST.barrier()


#1. Generate the codification for all positions (its is convert to binary information all positions)
for ii in range(0, int(S_lengthi/2)):
    
#    pdb.set_trace()  #to debug
    x = str(bin(ii))
    x = x[2:] #to erase innecesary information in the binary str
     
    f = P_N - len(x) #Compute the difference between the max binary len and each binary element
    
    if f < P_N and f >0: #Add zeros to each binary str that has a len less than the max len
        for i in range(0, f):
            x = "0" + x 
            
    #-----Convert the integer signal values to binary representation-----
    S_odd = bin(int(Signal[2*ii+1])) #Store the odd elements of the signal
    S_odd = S_odd[2:]
    
    S_even = bin(int(Signal[2*ii])) #Store the even elements of the signal
    S_even = S_even[2:]
    
    if len(S_odd) < Bit_Precision:
        f_odd = Bit_Precision - len(S_odd)
        
        for i in range (0, f_odd):
            S_odd = "0" + S_odd
            
    if len(S_even) < Bit_Precision:
        f_even = Bit_Precision - len(S_even)
        
        for i in range (0, f_even):
            S_even = "0" + S_even
    #---------------------------------------------------------------------
    
    #2. Gate addition for the signal positions (put the X or I gates to generate the positions)
    for i in range(0, P_N):
        if x[i]=='0':
            circuit_ST.x(X_position[P_N + aux_q-1-i]) #Add a X-gate
            'Note: to access to the position qubits, the counting need to start at reversed order'
        else:
            circuit_ST.i(X_position[P_N + aux_q-1-i]) #Add a I-gate
    #---------------------------------------------------------------------
    circuit_ST.barrier()
    
    #3. Generate the CCNOT conections between the X position and the X-auxiliary qubits 
    j = 0;
    for jj in range(Number_position-1, 1, -2):
        j=j+1;
        circuit_ST.ccx(X_position[jj], X_position[jj-1], X_position[aux_q-j])
        'Note: the aux qubits are those where the X-gate, in the CC-NOT, is applied' 
    #---------------------------------------------------------------------
    
    #4. Generate the CNOT conecction to each binary representation of the signal
    #(To store the element values of the signal)
    if P_N < 2:
        for i in range(0, Bit_Precision):
            #To store the even elements
            if S_even[i]=='1':
                circuit_ST.cx(X_position[0], even_e[Bit_Precision-1-i])
            #To store the odd elements
            if S_odd[i]=='1':
                circuit_ST.cx(X_position[0], odd_e[Bit_Precision-1-i])        
    else:
        for i in range(0, Bit_Precision):
            #To store the even elements
            if S_even[i]=='1':
                circuit_ST.ccx(X_position[1], X_position[0], even_e[Bit_Precision-1-i])
            #To store the odd elements
            if S_odd[i]=='1':
                circuit_ST.ccx(X_position[1], X_position[0], odd_e[Bit_Precision-1-i])
    #---------------------------------------------------------------------
    
     #3. Generate the CCNOT conections between the X position and the X-auxiliary qubits
    #This is for undo these operations and clean the auxiliary qubits
    j = 0;
    for jj in range(Number_position-1, 1, -2):
        j=j+1;
        circuit_ST.ccx(X_position[jj],X_position[jj-1], X_position[aux_q-j])
        'Note: the aux qubits are those where the X-gate, in the CC-NOT, is applied'
    #---------------------------------------------------------------------
    circuit_ST.barrier()
    
    #2. Gate addition for the signal positions (put the X or I gates to generate the positions)
    for i in range(0, P_N):
        if x[i]=='0':
            circuit_ST.x(X_position[P_N+ aux_q-1-i]) #Add a X-gate
            'Note: to access to the position qubits, the counting need to start at reversed order'
        else:
            circuit_ST.i(X_position[P_N + aux_q-1-i]) #Add a I-gate
    #---------------------------------------------------------------------
    circuit_ST.barrier()
    
    #pdb.set_trace()  #to debug
    

#----------Operations ST----------
'-----Addtion-----'
for ii in range(0, Bit_Precision):
    circuit_ST.append(csxdg_gate, [even_e[ii], add_q[ii+1]])
    circuit_ST.append(csxdg_gate, [odd_e[ii] , add_q[ii+1]])
    circuit_ST.append(csxdg_gate, [add_q[ii] , add_q[ii+1]])
    
    circuit_ST.cx(odd_e[ii] , even_e[ii])
    circuit_ST.cx(even_e[ii], add_q[ii])
    circuit_ST.cx(odd_e[ii] , even_e[ii])
    
    circuit_ST.csx(add_q[ii], add_q[ii+1])
    
    circuit_ST.barrier()
    
'-----Rounding and Halving-----'
#---Odd/Even Selection---
circuit_ST.swap(add_q[0], OE)

#---Halving operation---
for ii in range(0, Bit_Precision):
    circuit_ST.swap(add_q[ii], add_q[ii+1])
circuit_ST.barrier()

'-----Subtraction-----'
'Sub: position 0'
circuit_ST.append(csxdg_gate, [even_e[0], sub_q[0]])
circuit_ST.cx(odd_e[0]  , even_e[0])
circuit_ST.csx(odd_e[0] , sub_q[0])
circuit_ST.csx(even_e[0], sub_q[0])
circuit_ST.barrier()

'Sub: position i'
for ii in range(1, Bit_Precision):
    circuit_ST.append(csxdg_gate, [even_e[ii], sub_q[ii]])
    circuit_ST.cx(odd_e[ii] , even_e[ii])
    circuit_ST.csx(odd_e[ii], sub_q[ii])
    
    circuit_ST.cx(sub_q[ii-1] , even_e[ii])
    circuit_ST.csx(sub_q[ii-1], sub_q[ii])
    circuit_ST.csx(even_e[ii] , sub_q[ii])
    
    circuit_ST.barrier()

#Measuring
'Sub'
#To measure the output of the subtration operation, all the X_position, the even-variables and the last sub_q element 
#must be measured in that order
#circuit_ST.measure([X_position[0], X_position[1], even_e[0], even_e[1], sub_q[1]], [0,1,2,3,4])
#circuit_ST.measure([X_position[1], X_position[2], X_position[3], even_e[0], even_e[1], even_e[2], sub_q[2]], [0,1,2,3,4,5,6])

'Add'
#Measure the X_positions, and the add_q variables
#circuit_ST.measure([X_position[1], X_position[2], X_position[3], add_q[0], add_q[1], add_q[2], add_q[3]],  [0,1,2,3,4,5,6])

#Circuit drawing
circuit_ST.draw(output='mpl')    

