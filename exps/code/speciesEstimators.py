# Module containing species estimators
import math

# Compute Chao1 estimator based on abundance data
def chao1Estimate(sample):

    # find element counts

    elementCounts = {}
    for e in sample:
        if e not in elementCounts:
            elementCounts[e] = 1.0
        else:
            elementCounts[e] += 1.0

    # compute Sobs, fValues
    Sobs = len(elementCounts)
    fValues = {}
    for e in elementCounts:
        if elementCounts[e] not in fValues:
            fValues[elementCounts[e]] = 1.0
        else:
            fValues[elementCounts[e]] += 1.0

    Schao1 = 0.0
    Schao1Var = 0.0

    if 1.0 in fValues:
        f1 = fValues[1.0]
    else:
        f1 = 0.0
    if 2.0 in fValues:
        f2 = fValues[2.0]
    else:
        f2 = 0.0

    n = float(len(sample))

    if f1 > 0.0 and f2 > 0.0:
        Schao1 = Sobs + ((n-1)/n)*f1*(f1-1)/(2*(f2+1))
        Schao1Var = f1*(f1-1.0)/2 + f1*((2*f1-1)**2)/(4*((f2+1)**2)) + (f1**2)*f2*((f1-1)**2)/(4*((f2+1)**2))
    elif f1 > 1.0 and f2 == 0.0:
        Schao1 = Sobs + ((n-1)/n)*f1*(f1-1)/(2*(f2+1))
        Schao1Var = f1*(f1-1)/2 + f1*((2*f1 - 1)**2)/4 - (f1**4)/(4*Schao1)
    else:
        Schao1 = Sobs
        Schao1varSum1 = 0.0
        Schao1varSum2 = 0.0
        for v in fValues:
            Schao1varSum1 += fValues[v]*(math.exp(-1.0*v) -math.exp(-2.0*v))
            Schao1varSum2 += v*math.exp(-1.0*v)*fValues[v]
        Schao1Var = Schao1varSum1 - (Schao1varSum2**2)/n

    return Schao1, Schao1Var


# Compute Chao1 estimator based on abundance data
def chao2Estimate(sampleList):

    # find element counts
    elementCounts = {}
    for sample in sampleList:
        for e in sample:
            if e not in elementCounts:
                elementCounts[e] = 1.0
            else:
                elementCounts[e] += 1.0

    # compute Sobs, QValues
    Sobs = len(elementCounts)
    QValues = {}
    for e in elementCounts:
        if elementCounts[e] not in QValues:
            QValues[elementCounts[e]] = 1.0
        else:
            QValues[elementCounts[e]] += 1.0

    Schao2 = 0.0
    Schao2Var = 0.0

    if 1.0 in QValues:
        Q1 = QValues[1.0]
    else:
        Q1 = 0.0
    if 2.0 in QValues:
        Q2 = QValues[2.0]
    else:
        Q2 = 0.0

    m = float(len(sampleList))

    if Q1 > 0.0 and Q2 > 0.0:
        Schao2 = Sobs + ((m-1)/m)*Q1*(Q1-1)/(2*(Q2+1))
        Schao2Var = ((m-1)/m)*Q1*(Q1-1.0)/(2*Q2+1) + (((m-1)/m)**2)*Q1*((2*Q1-1)**2)/(4*((Q2+1)**2)) + (((m-1)/m)**2)*(Q1**2)*Q2*((Q1-1)**2)/(4*((Q2+1)**2))
    elif Q1 > 0.0 and Q2 == 0.0:
        Schao2 = Sobs + ((m-1)/m)*Q1*(Q1-1)/(2*(Q2+1))
        Schao2Var = ((m-1)/m)*Q1*(Q1-1)/2 + (((m-1)/m)**2)*Q1*((2*Q1 - 1)**2)/4 - (((m-1)/m)**2)*(Q1**4)/(4*Schao2)
    else:
        Schao2 = Sobs
        Schao2varSum1 = 0.0
        Schao2varSum2 = 0.0
        for v in QValues:
            Schao2varSum1 += QValues[v]*(math.exp(-1.0*v) -math.exp(-2.0*v))
            Schao2varSum2 += v*math.exp(-1.0*v)*QValues[v]
        Schao2Var = Schao2varSum1 - (Schao2varSum2**2)/m

    return Schao2, Schao2Var


# Compute Chao estimator based on abundance data
def chao92Estimate(sample):

    # find element counts

    elementCounts = {}
    for e in sample:
        if e not in elementCounts:
            elementCounts[e] = 1.0
        else:
            elementCounts[e] += 1.0

    # compute Sobs, fValues
    Sobs = len(elementCounts)
    fValues = {}
    for e in elementCounts:
        if elementCounts[e] not in fValues:
            fValues[elementCounts[e]] = 1.0
        else:
            fValues[elementCounts[e]] += 1.0

    if 1.0 in fValues:
        f1 = fValues[1.0]
    else:
        f1 = 0.0
    if 2.0 in fValues:
        f2 = fValues[2.0]
    else:
        f2 = 0.0

    n = float(len(sample))

    Chat = 1 - f1/n
    gammaSum = 0.0
    if (Chat == 0):
        return Sobs, 0.0

    for v in fValues:
         gammaSum += v*(v-1)*fValues[v]

    gamma = (Sobs/Chat)*gammaSum/(n*(n-1)) - 1
    gamma = max(gamma,0)
    SChao92 = Sobs/Chat + n*(1-Chat)*gamma/Chat

    # Compute variance
    SChao92Var = 0.0
    if (gamma > 0):
        sumFi = 0
        sumiFi = 0
        sumii_oneFi = 0

        for i in fValues:
            sumFi += fValues[i]
            sumiFi += i*fValues[i]
            sumii_oneFi += i*(i-1)*fValues[i]

        # Compute derivatives
        dFvalues = {}

        a = sumFi - f1
        n = sumiFi - f1
        b = sumii_oneFi - f1

        dFvalues[1.0] = a*(b*(f1**2 + 2*f1*(n-1) + (n-1)*n) + n*(f1+n-1)**2 + b*f1*(2*f1**2 + f1*(4*n -3) + 2*(n-1)*n))/ (n**2 *(f1 + n -1)**2)
        fValues[1.0] = f1

        for i in fValues:
            if (i == 1.0):
                continue
            a = sumFi - fValues[i]
            b = sumiFi - i*fValues[i]
            g = sumii_oneFi - i*(i-1)*fValues[i]
            k = i*(i-1)
            f = fValues[i]

            dFvalues[i] = (1/b**2)*((b + f)**2)*((b*f1*(a*(g*(-2*b - 2*f + f1 + 1) - f1*(-1.0*(b**2) + b*f1 + b + f**2 - f1)) + b**2*(2*f*f1 + g)- b*(2*f*f1*(-f + f1 + 1) + g*(f1+1)) - f**2*g - (f**2)*(f1**2) - f**2*f1 + 2*f*f1**2 + g*f1))/((b+f-1)**2*(b+f)*(b+f-f1)**2)+(b*f1*(((a+f)*(f*f1+g))/((b+f-1)*(b+f-f1)) - 1))/(b+f)**2 + b*(a+f)/((b+f)**2) -f/(b+f) + 1)

        for i in dFvalues:
            for j in dFvalues:
                if i == j:
                    SChao92Var += dFvalues[i]*dFvalues[j]*fValues[i]*(1-fValues[i]/SChao92)
                else:
                    SChao92Var += dFvalues[i]*dFvalues[j]*(-1.0*fValues[i]*fValues[j]/SChao92)

    return SChao92, SChao92Var