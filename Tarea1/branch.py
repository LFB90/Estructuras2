import sys
import os
import argparse
import time
import re

def choose (predA,predB,outcome,counter,switch):
    temp=switch
    if(counter=='00' or counter == '01'):
        switch='P'
    if(counter=='11' or counter == '10'):
        switch='G'
    if(predA==predB==outcome):
        switch=temp
    if(predA==outcome):
        counter=nextPHC(counter,'N')
    if(predB==outcome):
        counter=nextPHC(counter,'T')
    
        
    return [switch,counter]

def prediction(counter):
    pred=''
    if(counter=='00'):
        pred='N'
    if(counter=='01'):
        pred='N'
    if(counter=='11'):
        pred='T'
    if(counter=='10'):
        pred='T'
    return pred

def nextPHC(counter,jump):
    
    newCounter=''
    #maquina de estados con shift left
    if(bool(jump == 'T') & bool(counter=='00')):
        newCounter='01'
    if(bool(jump == 'T') & bool(counter=='01')):
        newCounter='11'
    if(bool(jump == 'T') & bool(counter=='10')):
        newCounter='01'
    if(bool(jump == 'T') & bool(counter=='11')):
        newCounter='11'
    if(bool(jump == 'N') & bool(counter=='00')):
        newCounter='00'
    if(bool(jump == 'N') & bool(counter=='01')):
        newCounter='00'
    if(bool(jump == 'N') & bool(counter=='10')):
        newCounter='00'
    if(bool(jump == 'N') & bool(counter=='11')):
        newCounter='10'
    return newCounter

def nextC(counter,jump):
    newCounter=''
    #maquina de estados
    if(bool(jump == 'T') & bool(counter=='00')):
        newCounter='01'
    if(bool(jump == 'T') & bool(counter=='01')):
        newCounter='10'
    if(bool(jump == 'T') & bool(counter=='10')):
        newCounter='11'
    if(bool(jump == 'T') & bool(counter=='11')):
        newCounter='11'
    if(bool(jump == 'N') & bool(counter=='00')):
        newCounter='00'
    if(bool(jump == 'N') & bool(counter=='01')):
        newCounter='00'
    if(bool(jump == 'N') & bool(counter=='10')):
        newCounter='01'
    if(bool(jump == 'N') & bool(counter=='11')):
        newCounter='10'
    return newCounter
#Bimodal Predictor
def branchPredictor(args):
    #Strong Taken:      11
    #Taken:             10
    #Not Taken:         01
    #Strong Not Taken:  00
    #Concatenated as [index][0][1][...][n]
    spec = '{fill}{align}{width}{type}'.format(fill=0, align='>', width=args.s, type='b')
    typeP='Bimodal'
    sizeBHT=pow(2,args.s)
    
    #Contadores Resultado
    cTBranches=0
    cNBranches=0
    iCTBranches=0
    iCNBranches=0
    bht = []
    
    
    i=0
    while(i<sizeBHT):
        bht.append('00')
        i=i+1;
    
    #branching
    i=0
    #print('\tOutput:\n')
    for line in args.input:
        #input filtering
        address=re.search('.(.*.) ',line).group(1)
        outcome=re.search('. (.*.)',line).group(1)
        #binary filtering
        binary=bin(int(format(int(address),spec),base=2))
        sizeBin=len(binary)
        addBin=binary[sizeBin-args.s:sizeBin]
        addIndex=int(addBin,base=2)%sizeBHT
        
        
        if(i<args.countsPC):
            #print('Traceline:',line)
            #print(i,': ',line,'Address: ',address,'Jump:',outcome,'Bin:',addBin,addBin[27-args.s:27],len(addBin),'Decimal Index:',addIndex)
            #print('New Counter:',nextC(bht[int(format(int(line[9]),spec),base=2)%8],line[11]),'Index:',int(format(int(line[9]),spec),base=2)%8,'Prediccion:',prediction(bht[int(format(int(line[9]),spec),base=2)%8]))

            counter=bht[addIndex]
            
            pred=prediction(counter)
            

            #Classification and Counting
            if (outcome=='T'):
                
                if (pred == 'T'):
                    cTBranches=cTBranches+1
                if (pred=='N'):
                    iCTBranches=iCTBranches+1

            if (outcome=='N'):
                
                if (pred == 'T'):
                    iCNBranches=iCNBranches+1
                if (pred=='N'):
                    cNBranches=cNBranches+1
            #actualizar contador de la BHT segun LSB de address
            bht[addIndex]=nextP(counter,outcome)

            #print('Trace-Address:',address,'Trace-Outcome',outcome)
        else:
            #end of prediction
            break
        i=i+1
    
    
    
    #print('Result:',[typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches],'BHT:',bht)
    return [typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches,i]



#GlobalHistory Predictor

def gHPredictor(args):
    #Strong Taken:      11
    #Taken:             10
    #Not Taken:         01
    #Strong Not Taken:  00
    #Concatenated as [index][0][1][...][n]
    spec = '{fill}{align}{width}{type}'.format(fill=0, align='>', width=args.s, type='b')
    spec2 = '{fill}{align}{width}{type}'.format(fill=0, align='>', width=args.gh, type='b')
    typeP='GShare'
    sizeBHT=pow(2,args.s)
    cTBranches=0
    cNBranches=0
    iCTBranches=0
    iCNBranches=0
    bht = []
    
    ghtReg = format(0,spec2)
    
    #index='0'*args.s
    i=0
    while(i<sizeBHT):
        bht.append('00')
        
        i=i+1;
    
    #branching
    i=0
    #print('\tOutput:\n')
    for line in args.input:
        #input filtering
        address=re.search('.(.*.) ',line).group(1) #Hexadecimal Memory Address
        outcome=re.search('. (.*.)',line).group(1) #Output Taken or Not Taken
        #binary filtering
        binary=bin(int(format(int(address),spec),base=2))#Binary Mem Address
        sizeBin=len(binary)
        addBin=binary[sizeBin-args.s:sizeBin] #sliced binary 
        addIndex=int(addBin,base=2)%sizeBHT
        
        #ghtReg=addBin[args.s-args.gh:args.s] #Sliced Reg by gh size before shift left
        xorIndex=int(addBin,base=2)^int(ghtReg,base=2)
        
        ghtReg=ghtReg[1:len(ghtReg)]
        if(i<args.countsPC):
            #print('Traceline:',line)
            #print(i,': ',line,'Address: ',address,'Jump:',outcome,'Bin:',addBin,'Decimal Index:',addIndex,'GHTReg:',ghtReg,'XOR:',bin(xorIndex),'XORIndex:',xorIndex)
            #print('New Counter:',nextC(bht[int(format(int(line[9]),spec),base=2)%8],line[11]),'Index:',int(format(int(line[9]),spec),base=2)%8,'Prediccion:',prediction(bht[int(format(int(line[9]),spec),base=2)%8]))

            counter=bht[xorIndex]
            
            pred=prediction(counter)
            

            #Classification and Counting
            if (outcome=='T'):
                ghtReg=ghtReg+'1'
                
                if (pred == 'T'):
                    #pht[xorIndex]=phBuffer
                    cTBranches=cTBranches+1
                if (pred=='N'):
                    iCTBranches=iCTBranches+1

            if (outcome=='N'):
                ghtReg=ghtReg+'0'
                if (pred == 'T'):
                    iCNBranches=iCNBranches+1
                    #pht[xorIndex]=phBuffer
                if (pred=='N'):
                    cNBranches=cNBranches+1
            #actualizar contador de la BHT y PHT segun LSB del PC Counter
            bht[xorIndex]=nextC(counter,outcome)
            

            #print('Trace-Address:',address,'Trace-Outcome',outcome)
        else:
            #end of prediction
            break
        i=i+1
    
    
    
    #print('Result:',[typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches],'BHT:',bht,'PHT:',pht)
    return [typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches,i]

#Private History Predictor
def pHPredictor(args):
    #Strong Taken:      11
    #Taken:             10
    #Not Taken:         01
    #Strong Not Taken:  00
    #Concatenated as [index][0][1][...][n]
    spec = '{fill}{align}{width}{type}'.format(fill=0, align='>', width=args.s, type='b')
    spec2 = '{fill}{align}{width}{type}'.format(fill=0, align='>', width=args.ph, type='b')
    typeP='PShare'
    sizeBHT=pow(2,args.s)
    #Result Counters
    cTBranches=0
    cNBranches=0
    iCTBranches=0
    iCNBranches=0
    bht = [] #Branch history Table
    pht = [] #Private History Table
    

    #index='0'*args.s
    i=0
    while(i<sizeBHT):
        bht.append('00')
        pht.append(format(0,spec2))
        i=i+1;
    
    #branching
    i=0
    #print('\tOutput:\n')
    for line in args.input:
        #input filtering
        address=re.search('.(.*.) ',line).group(1)
        outcome=re.search('. (.*.)',line).group(1)
        #binary filtering
        binary=bin(int(format(int(address),spec),base=2))
        sizeBin=len(binary)
        addBin=binary[sizeBin-args.s:sizeBin]
        addIndex=int(addBin,base=2)%sizeBHT
        phBuffer=addBin[args.s-args.ph:args.s] #Sliced entry by ph size to save into PHT after shift left
        
        #phReg=format(int(pht[addIndex],base=2),spec) #Formatted sliced entry by s size from pht to use in XOR
        phReg=pht[addIndex] #Sliced index by ph size from pht to use in XOR
        
        
        ############################################
        newPhReg=phReg[1:len(phReg)]#69.29% Table
        #newPhReg=phBuffer[1:len(phBuffer)]#68.31 Branch
        ############################################
        xorIndex=int(addBin,base=2)^int(phReg,base=2)

        
        
        if(i<args.countsPC):
            #print('Traceline:',line)
            #print(i,': ',line,'Address: ',address,'Jump:',outcome,'Bin:',addBin,'Decimal Index:',addIndex,'PHT:',phBuffer,'phToXor:',phReg,'XOR:',bin(xorIndex),'SReg:',newPhReg)
            #print('New Counter:',nextC(bht[int(format(int(line[9]),spec),base=2)%8],line[11]),'Index:',int(format(int(line[9]),spec),base=2)%8,'Prediccion:',prediction(bht[int(format(int(line[9]),spec),base=2)%8]))

            counter=bht[xorIndex]
            pred=prediction(counter)
            

            #Classification and Counting
            if (outcome=='T'):
                
                newPhReg=newPhReg+'1'
                if (pred == 'T'):
                    #pht[xorIndex]=phBuffer
                    cTBranches=cTBranches+1
                if (pred=='N'):
                    iCTBranches=iCTBranches+1

            if (outcome=='N'):
                newPhReg=newPhReg+'0'
                if (pred == 'T'):
                    iCNBranches=iCNBranches+1
                    #pht[xorIndex]=phBuffer
                if (pred=='N'):
                    cNBranches=cNBranches+1
            
            
            #actualizar contador de la BHT y PHT segun LSB del PC Counter
            bht[xorIndex]=nextPHC(counter,outcome)
            pht[xorIndex]=newPhReg

            #print('Trace-Address:',address,'Trace-Outcome',outcome)
        else:
            #end of prediction
            break
        i=i+1
    
    
    
    #print('Result:',[typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches],'BHT:',bht,'PHT:',pht)
    return [typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches,i]

#Tournament History Predictor
def tournamentPredictor(args):
    #Strong Taken:      11
    #Taken:             10
    #Not Taken:         01
    #Strong Not Taken:  00
    #Concatenated as [index][0][1][...][n]
    spec = '{fill}{align}{width}{type}'.format(fill=0, align='>', width=args.s, type='b')
    spec2 = '{fill}{align}{width}{type}'.format(fill=0, align='>', width=args.ph, type='b')
    spec3 = '{fill}{align}{width}{type}'.format(fill=0, align='>', width=args.gh, type='b')
    typeP='Tournament'
    sizeBHT=pow(2,args.s)
    cTBranches=0
    cNBranches=0
    iCTBranches=0
    iCNBranches=0
    bht = [] #Branch H. Table
    pht = [] #Private Table
    tCounter='00'  #Tournament Counter
    ghtReg = format(0,spec3) #gshare bin register
    
    switch='P'
    #index='0'*args.s
    i=0
    while(i<sizeBHT):
        bht.append('00')
        pht.append(format(0,spec2))
        i=i+1;
    
    #branching
    i=0
    #print('\tOutput:\n')
    for line in args.input:
        #input filtering
        address=re.search('.(.*.) ',line).group(1)
        outcome=re.search('. (.*.)',line).group(1)
        #binary filtering
        binary=bin(int(format(int(address),spec),base=2))
        sizeBin=len(binary)
        addBin=binary[sizeBin-args.s:sizeBin]
        addIndex=int(addBin,base=2)%sizeBHT
        choice=['P','00']

        #XOR operations
        phBuffer=addBin[args.s-args.ph:args.s] #Sliced entry by ph size to save into PHT after shift left
        phReg=pht[addIndex] #Sliced index by ph size from pht to use in XOR
        xorIndex1=int(addBin,base=2)^int(phReg,base=2)  #PShare
        xorIndex2=int(addBin,base=2)^int(ghtReg,base=2) #GShare
        
        
        if(i<args.countsPC):
            #print('Traceline:',line)
            #print(i,': ',line,'Address: ',address,'Jump:',outcome,'Bin:',addBin,'Decimal Index:',addIndex,'PHT:',phBuffer,'phToXor:',phReg,'XOR1:',bin(xorIndex1),'XOR2:',bin(xorIndex2),'Switch:',switch,'SReg:',newPhReg)
            #print('New Counter:',nextC(bht[int(format(int(line[9]),spec),base=2)%8],line[11]),'Index:',int(format(int(line[9]),spec),base=2)%8,'Prediccion:',prediction(bht[int(format(int(line[9]),spec),base=2)%8]))
            
            #PShare
            counter1=bht[xorIndex1]
            pred1=prediction(counter1)

            #GShare
            counter2=bht[xorIndex2]
            pred2=prediction(counter2)

            choice=choose(pred1,pred2,outcome,tCounter,choice[0]) #[switch,newTournamentCounter]

            #Predictor Selection
            if(choice[0]=='P'):#PShare
                #Classification and Counting
                newPhReg=phReg[1:len(phReg)]
                if (outcome=='T'):
                    
                    newPhReg=newPhReg+'1'
                    if (pred1 == 'T'):
                        #pht[xorIndex]=phBuffer
                        cTBranches=cTBranches+1
                    if (pred1 =='N'):
                        iCTBranches=iCTBranches+1

                if (outcome=='N'):
                    newPhReg=newPhReg+'0'
                    if (pred1 == 'T'):
                        iCNBranches=iCNBranches+1
                        #pht[xorIndex]=phBuffer
                    if (pred1 =='N'):
                        cNBranches=cNBranches+1
                pht[xorIndex1]=newPhReg
                bht[xorIndex1]=nextC(counter1,outcome)
            if(choice[0]=='G'):#GShare
                ghtReg=ghtReg[1:len(ghtReg)]
                #Classification and Counting
                if (outcome=='T'):
                    
                    ghtReg=ghtReg+'1'
                    if (pred2 == 'T'):
                        #pht[xorIndex]=phBuffer
                        cTBranches=cTBranches+1
                    if (pred2 =='N'):
                        iCTBranches=iCTBranches+1

                if (outcome=='N'):
                    ghtReg=ghtReg+'0'
                    if (pred2 == 'T'):
                        iCNBranches=iCNBranches+1
                        #pht[xorIndex]=phBuffer
                    if (pred2 =='N'):
                        cNBranches=cNBranches+1
                bht[xorIndex2]=nextC(counter2,outcome)
            
            
            #actualizar contador de la BHT y PHT segun LSB del PC Counter
            
            tCounter=choice[1]

            #print('Trace-Address:',address,'Trace-Outcome',outcome)
        else:
            #end of prediction
            break
        i=i+1
    
    
    
    #print('Result:',[typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches],'BHT:',bht,'PHT:',pht)
    return [typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches,i]

def printPredictors(args,typeP,sizeBHT,cTBranches,iCTBranches,cNBranches,iCNBranches,i):
    
    print('------------------------------------------------------------------------')
    print('Prediction parameters:')
    print('------------------------------------------------------------------------')
    print('Branch prediction type:',typeP)
    print('BHT size (entries):',sizeBHT)
    print('Global history register size:',args.gh)
    print('Private history register size:',args.ph)
    print('------------------------------------------------------------------------')
    print('------------------------------------------------------------------------')
    print('Simulation results:')
    print('------------------------------------------------------------------------')
    print('Number of branches:',i)
    print('Number of correct predictions of taken branches:',cTBranches)
    print('Number of incorrect predictions of taken branches:',iCTBranches)
    print('Number of correct predictions of not-taken branches:',cNBranches)
    print('Number of incorrect predictions of not-taken branches:',iCNBranches)
    print('Percentage of correct predictions:',"{:.2f}".format((cTBranches+cNBranches)/args.countsPC*100))
    print('------------------------------------------------------------------------')
    print('Percentage of written predictions:','{:.2f}'.format((cTBranches+cNBranches+iCTBranches+iCNBranches)/args.countsPC*100),'(',cTBranches+cNBranches+iCTBranches+iCNBranches,'/',args.countsPC,')')

def branchP():
    
    parser=argparse.ArgumentParser()
    parser.add_argument('input',help='',type=argparse.FileType('r'),nargs='?',default=sys.stdin)
    parser.add_argument('-countsPC',help='',type=int,default=16416279)
    parser.add_argument('-s',help='',type=int,default=5)
    parser.add_argument('-bp',help='',type=int,default=0)
    parser.add_argument('-gh',help='',type=int,default=4)
    parser.add_argument('-ph',help='',type=int,default=3)
    args=parser.parse_args()

    
    #Bimodal
    if args.bp == 0:
        result=branchPredictor(args)
        printPredictors(args,result[0],result[1],result[2],result[3],result[4],result[5],result[6])
    #Private History
    if args.bp == 1:
        result=pHPredictor(args)
        printPredictors(args,result[0],result[1],result[2],result[3],result[4],result[5],result[6])
    #Global History
    if args.bp == 2:
        result=gHPredictor(args)
        printPredictors(args,result[0],result[1],result[2],result[3],result[4],result[5],result[6])

    #Tournament History
    if args.bp == 3:
        result=tournamentPredictor(args)
        printPredictors(args,result[0],result[1],result[2],result[3],result[4],result[5],result[6])
       




if __name__=="__main__":
    t1=time.time()
    #print('check')
    branchP()
    print('Runtime:',time.time()-t1,' seconds')