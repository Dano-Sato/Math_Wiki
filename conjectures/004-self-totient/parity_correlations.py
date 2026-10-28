"""004 D028: a_n 홀짝과 단순 산술 함수의 상관. 입력은 parity_mean_bound.go의 이진 출력.

    python parity_correlations.py a.bin
"""
import sys
import numpy as np
a=np.fromfile(sys.argv[1],dtype=np.uint32).astype(np.int64); N=len(a)-1
n=np.arange(N+1)
spf=np.zeros(N+1,dtype=np.int32)
for p in range(2,int(N**0.5)+1):
    if spf[p]==0:
        idx=np.arange(p*p,N+1,p); m=spf[idx]==0; spf[idx[m]]=p
z=(spf==0); spf[z]=n[z]
# Omega, omega
Om=np.zeros(N+1,np.int8); om=np.zeros(N+1,np.int8); sqf=np.ones(N+1,bool)
x=n.copy(); last=np.zeros(N+1,np.int64)
for it in range(30):
    act=x>1
    if not act.any(): break
    p=spf[x[act]]
    Om[act]+=1
    new=p!=last[act]; om_a=om[act]; om_a[new]+=1; om[act]=om_a
    sq=sqf[act]; sq[~new]=False; sqf[act]=sq
    last[act]=p; x[act]//=p
P=(a&1).astype(np.int64); s=1-2*P
lam=1-2*(Om%2); mu=np.where(sqf,1-2*(om%2),0)
O=np.cumsum(P); Opar=1-2*(np.concatenate([[0],O[:-1]])%2)
cls={'odd composite':(n%2==1)&(spf!=n)&(n>1),'even':(n%2==0)&(n>2)}
for name,m in cls.items():
    m[:1000]=False
    print(name,"count",m.sum(),"P(odd)",P[m].mean().round(5))
    for fn,f in [('lambda',lam),('mu',mu),('(-1)^omega',1-2*(om%2)),('n%4==1',np.where(n%4==1,1,-1)),('3|n',np.where(n%3==0,1,-1)),('(-1)^O(n)',Opar),('(-1)^a_{n-1}',np.concatenate([[1],s[:-1]]))]:
        print("   corr with",fn, np.round(np.mean(s[m]*f[m]),5))
