# Bibliotecas
import re #extrair partes da string 
import numpy as np #manipular matrizes e vetores
from itertools import combinations #verificar as combinações possíveis de colunas
import pandas as pd

#-----------------------------------------------------------------------------------------------------------------------------------------
def titulo (titulo, largura=168, caractere="="):
    print(titulo.center(largura))
    print(caractere * largura)

def imprimirvalores ():
    print("\033[94mIteração:\033[0m", iter)
    print("Variáveis Básicas (IB):", IB)
    print("Variáveis Não Básicas (In):", In)
    print("Valor de XB (solução básica):\n", XB)
    print("Valor da Função Objetivo:", FunObjSol)
    print("Custos relativos:\n", CustosRelativos)
    print("Valor Dual (pT): \n", pT)

def NovaBase ():
    print(f"Variável que vai entrar na base: X{IndiceMaisNegativo}")
    print(f"Variável que vai sair da base: X{VarSaiBase}")

#-----------------------------------------------------------------------------------------------------------------------------------------
#Lendo o arquivo txt para armazenar os dados corretamente nos vetores e matrizes
with open ('/home/paloma/Documents/Codigos/SimplexRevisado/Instâncias/instchat.txt','r') as arquivo:
    dados = [linha.strip() for linha in arquivo.readlines()] #linha.strip() para remover as quebras de linhas (\n)

QuantLinhas = len(dados)

FuncaoObjetivo = []
Restricoes = []
TipoVar = []

for i in range (0,QuantLinhas):
    if (i == 0):
        Tipo = dados[i]
    elif (i == 1):
        FuncaoObjetivo.append(dados[i])
    elif (i > 1 and i < (QuantLinhas-1)):
        Restricoes.append(dados[i])
    elif (i == (QuantLinhas-1)):
        TipoVar.append(dados[i])

Variaveis = re.findall(r'x\d+', FuncaoObjetivo[0]) #identificando quais são as variáveis de decisão
indicesX = [int(i) for i in re.findall(r'x(\d+)', FuncaoObjetivo[0])] 

termos = re.findall(r'([+-]?\s*(?:\d+(?:\.\d+)?\s*)?)(x\d+)', FuncaoObjetivo[0]) #identificando quais são os coeficientes da FO do problema original
coeficientes= []
for coef, var in termos:
    coef = coef.strip().replace(' ', '')
    if coef in ('', '+', '-'):
        coef += '1'
    if float(coef) == 0:
        coef = '0'
    coeficientes.append(coef)
CoefObjOriginal = np.array([float(coef) for coef in coeficientes]) 

CoefRestOriginal = [] #identificando os coeficientes das variáveis nas restrições do problema original 
for i in Restricoes:
    ListaTemp = [0.0]* len(Variaveis)
    valor = re.findall (r'([-+]?\s*\d*(?:\.\d+)?)\s*x(\d+)',i)

    for coef, indice in valor:
        coef = coef.replace(' ', '')
        if (coef == '') or (coef == "+"):
            coeficiente = 1.0
        elif (coef == '-'):
            coeficiente = -1.0
        else:
            coeficiente = float(coef)
        ListaTemp[int(indice) -1] = coeficiente

    CoefRestOriginal.append(ListaTemp)
CoefRestOriginal = np.array(CoefRestOriginal) #matriz com os coeficientes das variáveis nas restrições 

OperadoresOriginais = [] #identificando os operadores originais
for i in Restricoes:
    operador = re.search(r'(<=|>=|=)', i)
    OperadoresOriginais.append(operador.group())

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
IndVarAdicionais = []

for i in Restricoes:
    if '<=' in i:
        RestricaoAjustada = i.replace('<=', f' + x{Indice} =')
        FuncaoObjetivo.append(f'+ 0 x{Indice}')
        TipoVar.append(f'x{Indice} >= 0')
        IndVarAdicionais.append(Indice)
        Indice +=1
    elif '>=' in i:
        RestricaoAjustada = i.replace('>=', f' - x{Indice} =')
        FuncaoObjetivo.append(f'+ 0 x{Indice}')
        TipoVar.append(f'x{Indice} >= 0')
        IndVarAdicionais.append(Indice)
        Indice +=1
    else:
        RestricaoAjustada = i
    RestricoesPadrao.append(RestricaoAjustada)

FunObjAtualizada = [' '.join(FuncaoObjetivo)] #utilizei join apenas para unir em uma única linha a FO 

VerNotacao = int(input("Deseja ver o modelo na forma padrão? (1- Sim / 2- Não): " + "\n"))
if VerNotacao== 1:
    titulo("Modelo na Forma Padrão")
    print("Função objetivo: ", FunObjAtualizada)
    print("Restrições: ", RestricoesPadrao)
    print("Não negatividade: ", TipoVar)

#-----------------------------------------------------------------------------------------------------------------------------------------

titulo("Transformando o modelo padrão em notação matricial")
x = np.array(re.findall(r'x\d+', FunObjAtualizada[0])) #vetor variavéis de decisão

termos = re.findall(r'([+-]?\s*(?:\d+(?:\.\d+)?\s*)?)(x\d+)', FunObjAtualizada[0])
coeficientes= []
for coef, var in termos:
    coef = coef.strip().replace(' ', '')
    if coef in ('', '+', '-'):
        coef += '1'
    if float(coef) == 0:
        coef = '0'
    coeficientes.append(coef)
c = np.array([float(coef) for coef in coeficientes]) #vetor dos coeficientes da função objetivo

b = []
for i in RestricoesPadrao:
    valor = re.findall(r'=\s*([-]?\d+(?:\.\d+)?)', i)
    b.append(float(valor[0]))
b = np.array(b) # vetor das constantes limitantes

IterMax = np.size(x)
A = []
for i in RestricoesPadrao:
    ListaTemp = [0.0]* IterMax
    valor = re.findall (r'([-+]?\s*\d*(?:\.\d+)?)\s*x(\d+)',i)

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

epsilon = 1e-20

VerNotacao = int(input("Deseja ver a notação matricial do problema na forma padrão? (1- Sim / 2- Não): " + "\n"))
if VerNotacao== 1:
    print ("Vetor das variáveis de decisão (x): \n", x)
    print ("Vetor dos coeficientes da função objetivo (c): \n", c)
    print ("Vetor dos recursos (b): \n", b)
    print("Matriz de coeficientes das variáveis nas restrições [A]: \n", A)
#-----------------------------------------------------------------------------------------------------------------------------------------
#Determinando Ib e In
IB = []
In = []

for i in IndVarAdicionais:
    IB.append(i - 1)

for i in indicesX:
    In.append(i - 1)

B = np.array(A[:, IB]) #matriz base

identidade = np.eye(len(RestricoesPadrao))  # Matriz identidade

if len(IB) == len(RestricoesPadrao) and np.allclose(B, identidade):
    print("Base é a identidade. Usar Simplex padrão.")
else:
    print(" ")
    print("Não existem combinações possíveis que formam uma matriz identidade")

    #Ativando o Método das Duas Fases
    titulo("Inicializando o método das Duas Fases")

    #================================== Manipulação de strings adicionando as variáveis artificiais===================================
    FunObjArtificial = []
    RestricoesArtificiais = []
    IndVarArt = []
    for i in FuncaoObjetivo:
        coefzerado = re.sub(r'([+-]?\s*)(?:\d+(?:\.\d+)?\s*)?(x\d+)', r'\1 0 \2', i)
        coefzerado = re.sub(r'^\s+', '', coefzerado)
        FunObjArtificial.append(coefzerado)
    
    cont = len(x)+1
    for i in range (len(RestricoesPadrao)): #verificar quais restrições necessitam de variáveis artificiais
            segmentacao = re.split(r'(=)', RestricoesPadrao[i])
            esquerda = segmentacao[0].strip()
            operador = segmentacao[1]
            direita = segmentacao[2].strip()

            if (OperadoresOriginais[i] == ('=')):
                NovaRestr = f"{esquerda} + x{cont} = {direita}"
                IndVarArt.append(cont)
                RestricoesArtificiais.append(NovaRestr)
                FunObjArtificial.append(f'+ x{cont}')
                cont+=1
            elif (OperadoresOriginais[i] == ('>=')):
                NovaRestr = f"{esquerda} + x{cont} = {direita}"
                IndVarArt.append(cont)
                RestricoesArtificiais.append(NovaRestr)
                FunObjArtificial.append(f'+ x{cont}')
                cont+=1
            elif (OperadoresOriginais[i] == ('<=')):
                RestricoesArtificiais.append(RestricoesPadrao[i])

    FunObjArtificial = [' '.join(FunObjArtificial)] 

    termos = re.findall(r'([+-]?\s*(?:\d+(?:\.\d+)?\s*)?)(x\d+)', FunObjArtificial[0])
    coef_art= []
    for coef, var in termos:
        coef = coef.strip().replace(' ', '')
        if coef in ('', '+', '-'):
            coef += '1'
        if float(coef) == 0:
            coef = '0'
        coef_art.append(coef)

    #======================================= Estabelecendo o vetor c (coeficientes das variáveis na FO===============================
    c_art = np.array([float(coef) for coef in coef_art]) 

    #============================================ Identificando as variáveis de decisão==============================================
    x_Art = np.array(re.findall(r'x\d+', FunObjArtificial[0])) #vetor variavéis de decisão

    #===================================== Estabelecendo a matriz de coeficientes das variáveis nas restrições=======================
    IterMax = np.size(coef_art)

    A_Art = []
    for i in RestricoesArtificiais:
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
        A_Art.append(ListaTemp)
    A_Art= np.array(A_Art) 

    indicesgeral = []
    IB = []
    In = []

    for i in range(0, len(x)):
        indicesgeral.append(i)
    for i in IndVarArt:
        indicesgeral.append(i-1)
    
    
    for linha in range(A.shape[0]): #verificando as colunas que formam a identidade para determinar IB
        for j in range(A_Art.shape[1]):
            coluna = A_Art[:, j]
            if (coluna[linha] == 1.0) and (np.count_nonzero(coluna) == 1):
                IB.append(j)
                break

    for i in indicesgeral: #determinando In
        if i not in IB:
            In.append(i)

    #==================================================== Identificando a matriz base===============================================
    iter = 1
    while True:

        B = np.array(A_Art[:, IB]) 

        # print("Determinante:", np.linalg.det(B))
        InvB = np.linalg.inv(B) #inversa da matriz base 

        #=============================== Identificando os coeficientes das variáveis básicas na função objetivo=========================
        cB = c_art[IB] 

        #=============================================== Calculando a solução básica ===================================================
        XB = InvB @ b.reshape(-1, 1) 
        for i in range (0, len(XB)):
            valor = IB[i]

        #=============================================== Calculando a FO ===============================================================
        FunObjSol = cB @ XB 

        #============================ Calculando os custos relativos das variáveis não básicas==========================================
        pT = cB @ InvB 

        CustosRelativos = []
        for i in In:
            S = c_art[i] - (pT @ (A_Art[:, i].reshape(-1,1)))
            CustosRelativos.extend(S)
        
        VerResultados = int(input("Deseja ver os detalhes desta iteração no método de Duas Fases? (1- Sim / 2- Não): " + "\n"))
        if VerResultados == 1:
            imprimirvalores()

        #============================ Critério de parada caso todos os custos relativos >= 0==========================================
        var = len(CustosRelativos) 
        for i in range (0,len(CustosRelativos)):
            if CustosRelativos[i] >= (-epsilon):
                var-=1
        if var == 0:
            break
            
        #========================================== Verificando quem vai entrar na base=================================================
        analise = []
        indice = []
        for i in range (0, len(In)):
            if CustosRelativos[i] <= 0:
                analise.append(CustosRelativos[i])                                   
                indice.append(In[i])

        ValorMaisNegativo = min(analise)
        posicoes = [i for i, valor in enumerate(analise) if valor == ValorMaisNegativo]
        IndiceMaisNegativo = max(indice[i] for i in posicoes)

        #========================================== Verificando quem vai sair da base===================================================
        Y = InvB @ (A_Art[:, IndiceMaisNegativo].reshape(-1,1)) #calculando o Y = (B-1 * Ai) 

        cont = len(Y) #verificando se o problema é ilimitado
        for i in range (0,len(Y)):
            if Y[i] <= epsilon:
                cont-=1
        if cont == 0:
            break

        TesteRazao = []
        IndiceVar = []
        for j in range (0, XB.shape[0]):
            if Y[j] > epsilon:
                divisao = XB[j]/Y[j] 
                TesteRazao.extend(divisao)
                IndiceVar.append(IB[j])

        if len(TesteRazao) > 0 and all(x == TesteRazao[0] for x in TesteRazao):
            IndiceMax = max(IndiceVar)
            Indice = IndiceVar.index(IndiceMax)
        else:
            Minimo = min(TesteRazao) 
            Indice= TesteRazao.index(Minimo)
        VarSaiBase = IndiceVar[Indice] 

        if VerResultados == 1:
            NovaBase()

        #================================================ Atualizando IB e In==========================================================
        localbase = IB.index(VarSaiBase)
        IB[localbase] = IndiceMaisNegativo

        pos_in = In.index(IndiceMaisNegativo)
        In[pos_in] = VarSaiBase

        iter+=1

    for i in IndVarArt:
        for j in In:
            if (i-1) == j:
                In.remove(j)
                                                    #Procedimento Simplex 
#-----------------------------------------------------------------------------------------------------------------------------------------

titulo("Procedimento Simplex")
iter = 1
while True:

    B = np.array(A[:, IB]) #matriz base

    InvB = np.linalg.inv(B) #inversa da matriz base 

    cB = c[IB] #coeficientes das variáveis básicas na função objetivo

    XB = InvB @ b.reshape(-1, 1) #cálculo da solução básica (XB = B-1 * b)
    for i in range (0, len(XB)):
        valor = IB[i]

    FunObjSol = cB @ XB #calculando o valor da função objetivo da solução (f(x) = cB * XB)

    #Calculando os custos relativos das variáveis não básicas
    pT = cB @ InvB  #(pT = cB * B-1)


    CustosRelativos = []
    for i in In:
        S = c[i] - (pT @ (A[:, i].reshape(-1,1))) #(Si= ci - (pT * Ai))
        CustosRelativos.extend(S)

    VerResultados = int(input("Deseja ver os detalhes desta iteração? (1- Sim / 2- Não): " + "\n"))
    if VerResultados == 1:
        imprimirvalores()
        
    var = len(CustosRelativos) #adicionando o critério de parada caso todos os custos relativos >= 0
    for i in range (0,len(CustosRelativos)):
        if CustosRelativos[i] >= 0:
            var-=1
    if var == 0:
        print("Solução ótima encontrada")
        break
    
    #verificando quem vai entrar na base
    analise = []
    indice = []
    for i in range (0, len(In)):
        if CustosRelativos[i] <= (-epsilon):
            analise.append(CustosRelativos[i])                                   
            indice.append(In[i])

    ValorMaisNegativo = min(analise)
    posicoes = [i for i, valor in enumerate(analise) if valor == ValorMaisNegativo]
    IndiceMaisNegativo = max(indice[i] for i in posicoes)

    #verificando quem vai sair da base 
    Y = InvB @ (A[:, IndiceMaisNegativo].reshape(-1,1)) #calculando o Y = (B-1 * Ai) 

    cont = len(Y) #verificando se o problema é ilimitado
    for i in range (0,len(Y)):
        if Y[i] <= epsilon:
            cont-=1
    if cont == 0:
        break

    TesteRazao = []
    IndiceVar = []
    for j in range (0, XB.shape[0]):
        if Y[j] > epsilon:
            divisao = XB[j]/Y[j] #calculando o teste da razão (XB / Y)
            TesteRazao.extend(divisao)
            IndiceVar.append(IB[j])

    if len(TesteRazao) > 0 and all(x == TesteRazao[0] for x in TesteRazao):
        IndiceMax = max(IndiceVar)
        Indice = IndiceVar.index(IndiceMax)
    else:
        Minimo = min(TesteRazao) #verificando o valor mínimo do teste da razão (min {(XB / Y)})
        Indice= TesteRazao.index(Minimo)
    VarSaiBase = IndiceVar[Indice] #verificando quem sai da base

    if VerResultados == 1:
        NovaBase()

    #atualizando IB e In
    localbase = IB.index(VarSaiBase)
    IB[localbase] = IndiceMaisNegativo

    pos_in = In.index(IndiceMaisNegativo)
    In[pos_in] = VarSaiBase

    iter+=1

                                                    #Encontrando o Dual do Primal na forma padrão
#-----------------------------------------------------------------------------------------------------------------------------------------
RecursosDual = []
CoefObjDual = []
CoefRestDual = np.transpose(CoefRestOriginal)
VarDual = []

for i in CoefObjOriginal:
    RecursosDual.append(int(i))

for i in b:
    CoefObjDual.append(i)

for i in range(1, A.shape[0]+1):
    VarDual.append(f"p{i}")


RestricoesDual = [] #verificando quais são as restrições dual

for i in range (0, len(CoefRestDual)):
    ResDual = []
    for j in range (0, CoefRestOriginal.shape[0]):
        coef = float(CoefRestDual[i][j])
        if valor.is_integer():
            valor = int(valor)
        var = VarDual[j]

        if coef == 0 and var == "p1":
            termo = f"{coef}{var}"
        elif coef >= 0:
            termo = f"+{coef}{var}"
        else:
            termo = f"{coef}{var}"

        ResDual.append(termo)
    if Tipo == "minimizar":
        ResDual.append("<=")
    elif Tipo == "maximizar":
        ResDual.append(">=")

    ResDual += [str(RecursosDual[i])]
    ResDual = " ".join(ResDual)
    RestricoesDual.append(ResDual)

FunObjDual = []

for i in range (0, A.shape[0]):
    coef = int(CoefObjDual[i])
    var = VarDual[i]

    if coef >= 0 and var == "p1":
        termo = f"{coef}{var}"
    else:
        termo = f"+{coef}{var}"
    
    FunObjDual.append(termo)
FunObjDual = " ".join(FunObjDual)

RestVar = []
if Tipo == "minimizar":
    for i in range (len(Restricoes)):
        if '<=' in Restricoes[i]:
            RestVar.append(f'p{i+1} <= 0')
        elif '>=' in Restricoes[i]:
            RestVar.append(f'p{i+1} >= 0')
        elif '=' in Restricoes[i]:
            RestVar.append(f'p{i+1} livre')

elif Tipo == "maximizar":
    for i in range (len(Restricoes)):
        if '<=' in Restricoes[i]:
            RestVar.append(f'p{i+1} >= 0')
        elif '>=' in Restricoes[i]:
            RestVar.append(f'p{i+1} <= 0')
        elif '=' in Restricoes[i]:
            RestVar.append(f'p{i+1} livre')


                                                    #Gerando o arquivo txt com o Dual do Primal na forma padrão
#-----------------------------------------------------------------------------------------------------------------------------------------
titulo("Gerando o arquivo txt com o Dual")
with open ("Dual.txt", "w") as arquivo:
    if Tipo == "minimizar":
        arquivo.write("Maximizar\n")
    elif Tipo == "maximizar":
        arquivo.write("Minimizar\n")
    arquivo.write(FunObjDual)
    arquivo.write("\n")
    for i in RestricoesDual:
        arquivo.write(i)
        arquivo.write("\n")
    for i in RestVar:
        arquivo.write(i)
        arquivo.write("\n")
print("Dual exportado para o arquivo txt")

#-----------------------------------------------------------------------------------------------------------------------------------------
#solução ótima primal e dual

solucao_primal = {}
for i in range (len(IB)):
    if IB[i]+1 in indicesX:
        solucao_primal[f"x{IB[i]+1}"] = float(XB[i][0])
for i in range(len(In)):
    if (In[i]+1 in indicesX) and (f"x{In[i]+1}" not in solucao_primal):
        solucao_primal[f"x{In[i]+1}"] = 0.0


titulo("Solução ótima primal")
for i in sorted(solucao_primal.keys(), key=lambda x: int(x[1:])):
    print(f"{i} = {solucao_primal[i]}")
print(" ")


titulo("Solução ótima dual")
for i in range(0, len(pT)):
    print(f"{VarDual[i]} = {pT[i]}")
print(" ")

                                                    #Análise de Sensibilidade
#-----------------------------------------------------------------------------------------------------------------------------------------

ValoresX = []
for i in Variaveis:
    if i in solucao_primal:
        ValoresX.append(solucao_primal[i])
ValoresX = np.array(ValoresX)

ValorFinal = CoefRestOriginal @ ValoresX

DeltasInferior = []
DeltasSuperior = []

for i in range (len(XB)): 
    InvCol = InvB[:, i] #XB + B-1[delta 0 0]

    DeltaMin = []
    DeltaMax = []
    for j in range (len(XB)):
        xj = XB[j].item()
        dj = InvCol[j]

        if dj > 0:
            DeltaMin.append(-xj / dj)
        if dj < 0:
            DeltaMax.append(-xj / dj)

    DeltaInf = max(DeltaMin) if DeltaMin else -np.inf
    DeltaSup = min(DeltaMax) if DeltaMax else np.inf

    DeltasInferior.append(abs(DeltaInf))
    DeltasSuperior.append(DeltaSup)

RecursoMaximo = []
RecursoMinimo = []

for i in range (len(b)):
    if DeltasInferior[i] != np.inf:
        calculo = b[i] - DeltasInferior[i]
    else:
        calculo = np.inf
    RecursoMinimo.append(calculo)

    if DeltasSuperior[i] != np.inf:
        calculo2 = b[i] + DeltasSuperior[i]
    else:
        calculo2 = np.inf
    RecursoMaximo.append(calculo2)

dados = {
    "Número": list(range(1, len(Restricoes) + 1)),
    "Valor Final": ValorFinal,
    "Preço Sombra": abs(pT),
    "Recursos": b,
    "Permitido Aumentar": DeltasSuperior,
    "Permitido Reduzir": DeltasInferior,
    "Recurso Máximo": RecursoMaximo,
    "Recurso Mínimo": RecursoMinimo
}
# Criando o DataFrame
tabela = pd.DataFrame(dados)

# Exibindo a tabela
titulo("Análise de Sensibilidade")
print("# Tabela Restrições")
print(tabela.to_string(index=False))