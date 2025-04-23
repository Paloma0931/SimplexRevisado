# Bibliotecas
import re #extrair partes da string 
import numpy as np #manipular matrizes e vetores
from itertools import combinations #verificar as combinações possíveis de colunas

#-----------------------------------------------------------------------------------------------------------------------------------------
#Lendo o arquivo txt para armazenar os dados corretamente nos vetores e matrizes
with open ('/home/paloma/OtimizaçãoLinear/Simplex/Instâncias/Instancia1.txt','r') as arquivo:
    dados = [linha.strip() for linha in arquivo.readlines()] #linha.strip() para remover as quebras de linhas (\n)

QuantLinhas = len(dados)

FuncaoObjetivo = []
Restricoes = []
NaoNegatividade = []

for i in range (0,QuantLinhas):
    if (i == 0):
        Tipo = dados[i]
    elif (i == 1):
        FuncaoObjetivo.append(dados[i])
    elif (i > 1 and i < (QuantLinhas-1)):
        Restricoes.append(dados[i])
    elif (i == (QuantLinhas-1)):
        NaoNegatividade.append(dados[i])

Variaveis = re.findall(r'x\d+', FuncaoObjetivo[0]) #identificando quais são as variáveis de decisão


if Tipo == "maximizar": #trasformando a função objetivo pra forma padrão
    s = FuncaoObjetivo[0]
    if s[0] not in '+-': 
        s = '+' + s
    s = s.replace('+', 'TEMP')
    s = s.replace('-', '+')
    s = s.replace('TEMP', '-')
    FuncaoObjetivo[0] = s
#-----------------------------------------------------------------------------------------------------------------------------------------
#Adicionando variáveis de folga ou excesso, além de atualizar a função objetivo
RestricoesPadrao = []
Indice = len(Variaveis) + 1

for i in Restricoes:
    if '<=' in i:
        RestricaoAjustada = i.replace('<=', f' + x{Indice} =')
        FuncaoObjetivo.append(f'+ 0 x{Indice}')
        Indice +=1
    elif '>=' in i:
        RestricaoAjustada = i.replace('>=', f' - x{Indice} =')
        FuncaoObjetivo.append(f'+ 0 x{Indice}')
        Indice +=1
    else:
        RestricaoAjustada = i
    RestricoesPadrao.append(RestricaoAjustada)

FunObjAtualizada = [' '.join(FuncaoObjetivo)] #utilizei join apenas para unir em uma única linha a FO 

print(FunObjAtualizada)
print(RestricoesPadrao)
print(NaoNegatividade)

#-----------------------------------------------------------------------------------------------------------------------------------------
#Colocando os dados em notação matricial 
x = np.array(re.findall(r'x\d+', FunObjAtualizada[0])) #vetor variavéis de decisão

coef_string = re.findall(r'[+-]?\s*\d+(?:\.\d+)?(?=\s*x\d+)', FunObjAtualizada[0])
c = np.array([float(coef.replace(' ', '')) for coef in coef_string]) # vetor coeficientes da FO

b = []
for i in RestricoesPadrao:
    valor = re.findall(r'=\s*([-]?\d+(?:\.\d+)?)', i)
    b.append(float(valor[0]))
b = np.array(b) # vetor das constantes limitantes

IterMax = np.size(x)
A = []
for i in RestricoesPadrao:
    ListaTemp = [0.0]* IterMax
    valor = re.findall (r'([-+]?\s*\d*)\s*x(\d+)',i)

    for coef, indice in valor:
        coef = coef.replace(' ', '')
        if (coef == '') or (coef == "+"):
            coeficiente = 1.0
        elif (coef == '-'):
            coeficiente = -1.0
        else:
            coeficiente = float(coef)
        ListaTemp[int(indice) -1] = coeficiente

    A.append(ListaTemp)
A = np.array(A) #matriz com os coeficientes das variáveis nas restrições 
print(A)
#-----------------------------------------------------------------------------------------------------------------------------------------
#Determinando Ib e In
IB = []
In = []

identidade = np.eye(len(RestricoesPadrao)) #gerando a matriz identidade para comparar 

combinacoes = list(combinations(range(A.shape[1]), len(RestricoesPadrao))) #verificando todas as combinações possíveis das colunas  

for i in combinacoes: #verificar se essa combinação é igual a matriz identidade
    colunas = A[:, i]
    if (colunas == identidade).all(): #se for igual, variáveis básicas encontrada
        IB.extend(i)
        for j in range (0, len(x)): #verificando quem vai ser as variáveis não básicas
            if j not in IB:
                In.append(j)
if IB == []:
    print("Não existem combinações possíveis que formam uma matriz identidade")
        
                                                    #Procedimento Simplex 
#-----------------------------------------------------------------------------------------------------------------------------------------
print("base inicial", IB)

while True:
    print("nova base", IB)
    print("novo não básico", In)
    B = np.array(A[:, IB]) #matriz base

    print("Matriz B:")
    print(B)
    print("Determinante:", np.linalg.det(B))
    InvB = np.linalg.inv(B) #inversa da matriz base 

    cB = c[IB] #coeficientes das variáveis básicas na função objetivo

    XB = InvB @ b.reshape(-1, 1) #cálculo da solução básica (XB = B-1 * b)
    for i in range (0, len(XB)):
        valor = IB[i]
        print("Valor de X%d é: %.2f" % (valor, XB[i]))

    # input()
    FunObjSol = cB @ XB #calculando o valor da função objetivo da solução (f(x) = cB * XB)

    #Calculando os custos relativos das variáveis não básicas
    pT = cB @ InvB  #(pT = cB * B-1)

    CustosRelativos = []
    for i in In:
        print("custo de ci", c[i])
        S = c[i] - (pT @ (A[:, i].reshape(-1,1))) #(Si= ci - (pT * Ai))
        CustosRelativos.extend(S)
    print(CustosRelativos)

    var = len(CustosRelativos) #adicionando o critério de parada caso todos os custos relativos >= 0
    for i in range (0,len(CustosRelativos)):
        if CustosRelativos[i] >= 0:
            var-=1
    if var == 0:
        break
    
    #verificando quem vai entrar na base
    analise = []
    indice = []
    for i in range (0, len(In)):
        if CustosRelativos[i] <= 0:
            analise.append(CustosRelativos[i])                                   
            indice.append(In[i])

    ValorMaisNegativo = min(analise)
    posicao = analise.index(ValorMaisNegativo)
    IndiceMaisNegativo = indice[posicao]

    print("Custos Relativos:", analise)
    print("Valor mais negativo: ", ValorMaisNegativo)
    print("Variável que vai entrar na base:", f"X{IndiceMaisNegativo}")

    #verificando quem vai sair da base 
    Y = InvB @ (A[:, IndiceMaisNegativo].reshape(-1,1)) #calculando o Y = (B-1 * Ai) 
    print(Y)

    cont = len(Y) #verificando se o problema é infactível
    for i in range (0,len(Y)):
        if i < 0:
            cont-=1
    if cont == 0:
        "O problema é infáctivel"

    TesteRazao = []
    IndiceVar = []
    for j in range (0, XB.shape[0]):
        if Y[j] > 0:
            divisao = XB[j]/Y[j] #calculando o teste da razão (XB / Y)
            TesteRazao.extend(divisao)
            IndiceVar.append(IB[j])
    Minimo = min(TesteRazao) #verificando o valor mínimo do teste da razão (min {(XB / Y)})
    IndiceMin= TesteRazao.index(Minimo)
    VarSaiBase = IndiceVar[IndiceMin] #verificando quem sai da base

    print(TesteRazao)
    print("Valor mínimo: ", Minimo)
    print("Variável que sai da base:", f"X{VarSaiBase}")

    #atualizando IB e In
    localbase = IB.index(VarSaiBase)
    IB[localbase] = IndiceMaisNegativo

    pos_in = In.index(IndiceMaisNegativo)
    In[pos_in] = VarSaiBase








