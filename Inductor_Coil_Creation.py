from scipy.constants import c
from scipy.constants import pi
from math import sqrt



"""
Our desired resonance frequency is 18.75 MHz and the capacitance is in the 
range of 10-1000 pF (using 10, as its the minimum), the maximum possible 
inductance for our case is 7.20 μH.

Using: 
    w_0 = 1 / sqrt(L * C) -> L = 1 / (w_0 * C) -> L = 1 / (4 * pi * f_0 * C)

"""

def findMaxInductance(f_0, minCap):               #in Hz, F
    return 1 / (4 * pi**2 * f_0**2 * minCap)


"""
We wanted to fit the coil inside the bore of our magnet, which has an inner 
radius of 1.7 cm, and also we wanted the length of the coil, b, to be at least 
2.5 cm.

Variable 'a' is the inner radius, so we subtracted the wire width (thickness)
from our total 1.7 cm diameter. In theory, this would have been 1.37 cm. 
In practice, this became 1.1 cm.

Thus, 1.1 is also the diameter of the tube we will be using to wrap our wire 
around.

So our 'a', which is the radius, is 1.1 / 2, giving a = 0.55 cm.

We found 14 gauge wire to be the easiest to get a max inductance, given length
(b) constraints. Using the below functions, with b being nearly 2 inches (5 cm),
and n being 15.37 (we round up to 15.5 for a nice half turn) we get a max 
inductance of 1.9 μH, which is a quite a bit less than our maximum possible
inductance.

As an overview of our measurements thus far:
    f_0 = 18.75 MHz
    L = 1.9 μH
    d: 1.628 mm                         #nominal diameter of wire
    a = 0.55 cm
    b = 5 cm
    n = 15.5
"""

#general function for finding n and estimted wire width, given any desired 
#diameter a, length b, and inductance L

#Don't really need in the REPL
def wireWidth(a, b, L):
    n = ((23 * a + 25 * b) * L)**0.5 / a
    print("Estimated number of turns: ", n)
    wireWidth = b / (2 * n)
    print('Estimated wire width: ', wireWidth, ' cm')

def findL_n(a, b, d):
    wireWidth = 1000
    L = 0
    while wireWidth > d:  #width in cm
        L += .01
        n = sqrt(((23 * a + 25 * b) * L)) / a
        wireWidth = b / (2 * n)
    return L, n                     #L in μH

def Lbyf_0andCap(f_0, Cap):
    return 1 / (4 * pi**2 * f_0**2 * Cap) 
    
#can be used as a check on the above function. Given the L output from findL(),
#do we get our b-value of 5 cm?
def findBGivenL(a, d, L):    #give L in μH
    wireWidth = -1
    b = 0
    while wireWidth < d: #width in cm
        b += .01
        n = ((23 * a + 25 * b) * L)**0.5 / a
        wireWidth = b / (2 * n)
    print("Best b: ", b, " with ", n, " turns.")     #b in cm
    
def LbyGeo(n, a, b):
    L = ((n * a)**2) / (23 * a + 25 * b)
    return L
    
    
"""
Length of wire used in coil must be less than lambda/8 (eighth of the resonant 
wavelength).

2 * pi * a * n < lambda / 8  ->    2 * pi * a * n < c / 8 * f_0

As an overview of our measurements thus far:
    f_0 = 18.75 MHz
    L = 1.9 μH
    d: 1.628 mm                         #nominal diameter of wire
    a = 0.55 cm
    b = 5 cm
    n = 15.5
    l = 0.54 m

"""

#outputs give us l (coilLength, which we use in the next section)
def findCoilLength(a, n):
    return 2 * pi * (a / 100) * n


def isCoilLengthOkay(a, f_0, n):
    eighthWavelength = c / (8 * f_0)
    l = findCoilLength(a, n)
    return l < eighthWavelength


"""
To find our ideal tuning and matching capacitors, we used the followed methods,
from page 414 of Experimental Pulse NMR: A Nuts and Bolts Approach.

Equations used:
   Q = w_0 * L / R             #where w_0 is the angular resonance frequencies
   w**2 * L * C_t = 1          #where w = w_0
   Q * w * L * C_t**2 / (C_t + C_m)**2 = 50    #where w = w_0
   
When solving the last equation to find C_m:
   C_m = sqrt((Q * w * L * C_t**2) / 50) - C_t
   
Using all of our previously defined variables, alongside a new variable, R 
(wire resistance), we achieved the following capacitances:
    
    C_t = 38 pF
    C_m = 13 nF
    
As an overview of our measurements thus far:
    f_0 = 18.75 MHz
    L = 1.9 μH
    d: 1.628 mm                         #nominal diameter of wire
    a = 0.55 cm
    b = 5 cm
    n = 15.5
    l = 0.54 m
    R = 0.009 Ohms
    

"""

#inputs are the length and nominal diameter of wire used
def findCopperResistance(l, d):
    return 4 * l * 0.0171 / (pi * (d * 10)**2)

def findQualityFactor(f_0, L, R):       #L input in μH, but converted to Henries
    w_0 = 2 * pi * f_0
    return w_0 * L * 10**(-6) / R

def findC_t(f_0, L):                    #L input in μH, but converted to Henries
    w_0 = 2 * pi * f_0
    return 1 / (L * 10**(-6) * w_0**2)

def findC_m(f_0, L, R):                 #L input in μH, but converted to Henries
    Q = findQualityFactor(f_0, L, R)
    C_t = findC_t(f_0, L)
    w_0 = 2 * pi * f_0
    return sqrt((Q * w_0 * L * 10**(-6) * C_t**2) / 50) - C_t


#don't really need in the REPL
def getCapacitors(f_0, L, R):
    Q = findQualityFactor(f_0, L, R)
    C_t = findC_t(f_0, L)
    C_m = findC_m(f_0, L, R)
    print("Calculated Quality Factor: ", Q)
    print("Calculated C_t: ", C_t)
    print("Calculated C_m: ", C_m)
    
    
def simplePrintVariables(fullPrintCondition, f_0, minCap, a, b, d, maxL, L, n, l, R, Q, C_t, C_m):
    print("Resonance Frequency (Hz, variable name 'f_0'): ", f_0)
    print("Minimum capacitance (F, variable name 'minCap'): ", minCap)
    print("Inner Coil Radius (cm, variable name 'a'): ", a)
    print("Coil length (cm, variable name 'b'): ", b)
    print("Nominal wire width (cm, variable name 'd'): ", d)
    
    if fullPrintCondition:
        print("Maximum inductance (μH): ", maxL)
        print("Calculated inductance (μH): ", L)
        print("Number of turns needed: ", n)
        print("Length of wire needed (m): ", l)
        print("Resistance of wire (Ohms): ", R)
        print("Quality Factor: ", Q)
        print("Tuning Capacitor (F): ", C_t)
        print("Matching Capacitor (F): ", C_m)
    
def runOptimization():
    function_done = False
    hasBeenOptimized = False
    menu = """
    *********************************************************************
    This REPL is used to streamline and automize the process of RF 
    Probe creation. Below you'll find a list of things you can do. To 
    select one, enter the option you want after the promt. Case doesn't
    matter.
            
    The program starts by asking for the desired resonance for the 
    system, mimimum capacitance owned, inner radius of the coil, length
    of the coil, and nominal wire diameter. From those four variable, 
    the script will calculate the rest.
            
            E: print the variable used and their current values. Use this 
                option to also edit them.
            R: Runs the optimization process using the assigned values.
            P: Re-prints this menu and any variables currently defined.
            Q: Stops and quits the function.
    *********************************************************************        
            """
    print(menu)
    beginChoice = input("Begin program? Saying No will quit the program. y or n: ").lower()
    if beginChoice == "y":
        f_0 = float(input("Please enter the desired resonance frequency in Hz: "))        
        minCap = float(input("Please enter the mimimum capacitance you have (F): "))        
        a = float(input("Please enter the desired internal coil radius in cm (a): "))        
        b = float(input("Please enter the desired coil length in cm (b): "))        
        d = float(input("And finally, please enter the nominal wire width of the wire gauge chosen for the coil (cm): "))
    else:
        return
        
    maxL = None
    L = None
    n = None
    l = None
    R = None
    Q = None
    C_t = None
    C_m = None
    
    while not function_done:
        choice = input("""
    ***
    Please make an option from the menu printed above. Remember you can always 
    type 'p' to re-print the menu: 
    ***
                       """).lower()
            
        if choice == "e":
            simplePrintVariables(False, f_0, minCap, a, b, d, maxL, L, n, l, R, Q, C_t, C_m)
                
            editChoice = input("""
    ***
    Would you like to change any of these variables? Type y for yes or n for no.: 
    ***
                               """).lower()
            
            if editChoice == "y":
                varChangeChoice = input("""
    ***
    Which variable would you like to change? Type in one of the names listed 
    above in exactly the same way as it is printed in the parentheses: 
    ***
                                        """)
                if varChangeChoice == "f_0":
                    varChangeValue = float(input("What would you like it to be changed to? Please give value in Hz: "))
                    f_0 = varChangeValue
                    
                elif varChangeChoice == "minCap":
                    varChangeValue = float(input("What would you like it to be changed to? Please give value in F: "))
                    minCap = varChangeValue
                    
                elif varChangeChoice == "a":
                    varChangeValue = float(input("What would you like it to be changed to? Please give value in cm: "))
                    a = varChangeValue
                    
                elif varChangeChoice == "b":
                    varChangeValue = float(input("What would you like it to be changed to? Please give value in cm: "))
                    b = varChangeValue
                    
                elif varChangeChoice == "d":
                    varChangeValue = float(input("What would you like it to be changed to? Please give value in cm: "))
                    d = varChangeValue
                
            elif editChoice == "n":
                continue
            
            else:
                print("""
    ***
    Please try again using only the single letters y for yes and n for no 
    (case insensitive).
    ***
                      """)
            
        elif choice == "r":
            maxL = findMaxInductance(f_0, minCap)
            L, n = findL_n(a, b, d)
            l = findCoilLength(a, n)
            if not isCoilLengthOkay(a, f_0, n):
                print("""          
    ***
    Warning: Estimated length of wire needed exceeds an eighth of a wavelength.
    ***         
                """)
                
            R = findCopperResistance(l, d)
            Q = findQualityFactor(f_0, L, R)
            C_t = findC_t(f_0, L)
            C_m = findC_m(f_0, L, R)
            
            hasBeenOptimized = True
            
            simplePrintVariables(hasBeenOptimized, f_0, minCap, a, b, d, maxL, L, n, l, R, Q, C_t, C_m)
            
        elif choice == "p":
            print(menu)
            simplePrintVariables(hasBeenOptimized, f_0, minCap, a, b, d, maxL, L, n, l, R, Q, C_t, C_m)
            
        elif choice == "q":
            function_done = True
            
        else:
            print("""
    ***
    Please choose only one of the choices listed, using a single letter. Case 
    does not matter.
    ***
                  """)
            
            
            
runOptimization()
            
            
            