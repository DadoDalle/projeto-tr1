# imports necessários
import math
import definicoes

# definições globais modificaveis a partir do arquivo definicoes.py
AMOSTRAS_POR_BIT = definicoes.AMOSTRAS_POR_BIT
VOLTAGEM = definicoes.VOLTAGEM

################################################### Modulações Digitais ###########################################

# recebe uma lista de bits e o tipo de modulação, retorna a lista de níveis de tensão
def codificar_banda_base(bits: list[int], tipo: str) -> list[float]:

    # transforma em maiúsculas
    tipo = tipo.upper() 

    # descobre o tipo e chama a função correta
    if tipo == 'NRZ-POLAR':
        return _codificar_nrz_polar(bits)
    elif tipo == 'MANCHESTER':
        return _codificar_manchester(bits)
    elif tipo == 'BIPOLAR':
        return _codificar_bipolar(bits)
    else:
        raise ValueError(f"Tipo de modulação banda base desconhecido: {tipo}")

# NRZ-POLAR: Bit 1 -> +V, Bit 0 -> -V   
def _codificar_nrz_polar(bits: list[int]) -> list[float]:
    # resultado
    sinal = []

    # percorre todos os bits da lista de entrada
    for bit in bits:
        if bit == 1:
            nivel = VOLTAGEM
        else:
            nivel = -VOLTAGEM
        
        # adiciona a voltagem correspondente ao bit, repetida AMOSTRAS_POR_BIT vezes
        sinal.extend([nivel] * AMOSTRAS_POR_BIT)
    return sinal

# Manchester: Bit 1 -> Alto para Baixo (+V na 1ª metade, -V na 2ª metade), Bit 0 -> Baixo para Alto (-V na 1ª metade, +V na 2ª metade)
def _codificar_manchester(bits: list[int]) -> list[float]:
    # resultado
    sinal = []

    # divide o número de amostras por bit ao meio
    meio_periodo = AMOSTRAS_POR_BIT // 2
    
    # percorre todos os bits da lista de entrada
    for bit in bits:
        if bit == 1:
            # Alto -> Baixo
            sinal.extend([VOLTAGEM] * meio_periodo)
            sinal.extend([-VOLTAGEM] * meio_periodo)
        else:
            # Baixo -> Alto
            sinal.extend([-VOLTAGEM] * meio_periodo)
            sinal.extend([VOLTAGEM] * meio_periodo)
    return sinal

# Bipolar: Bit 1 -> Alterna entre +V e -V, Bit 0 -> 0V
def _codificar_bipolar(bits: list[int]) -> list[float]:
    # resultado
    sinal = []
    
    # controle do ultimo bit 1, começa falso para iniciar com +V
    ultimo_um_foi_positivo = False
    
    # percorre todos os bits da lista de entrada
    for bit in bits:
        if bit == 0:
            nivel = 0.0
        else:
            if ultimo_um_foi_positivo:
                nivel = -VOLTAGEM
                ultimo_um_foi_positivo = False
            else:
                nivel = VOLTAGEM
                ultimo_um_foi_positivo = True
                
        sinal.extend([nivel] * AMOSTRAS_POR_BIT)
    return sinal

################################################### Demodulações Digitais ###########################################

# recebe o sinal modulado e o tipo de modulação, retorna a lista de bits original
def decodificar_banda_base(sinal_niveis: list[float], tipo: str) -> list[int]:

    # transforma em maiúsculas
    tipo = tipo.upper()
    
    # Verifica se o sinal tem um número correto de amostras
    if len(sinal_niveis) % AMOSTRAS_POR_BIT != 0:
        print("Aviso: O sinal recebido pode estar incompleto ou dessincronizado.")

    # descobre o tipo e chama a função correta
    if tipo == 'NRZ-POLAR':
        return _decodificar_nrz_polar(sinal_niveis)
    elif tipo == 'MANCHESTER':
        return _decodificar_manchester(sinal_niveis)
    elif tipo == 'BIPOLAR':
        return _decodificar_bipolar(sinal_niveis)
    else:
        raise ValueError(f"Tipo de decodificação banda base desconhecido: {tipo}")

# Decodificação NRZ-Polar: Média positiva -> 1, Média negativa -> 0
def _decodificar_nrz_polar(sinal: list[float]) -> list[int]:
    # resultado
    bits = []

    # percorre o sinal em blocos de AMOSTRAS_POR_BIT
    for i in range(0, len(sinal), AMOSTRAS_POR_BIT):
        bloco = sinal[i : i + AMOSTRAS_POR_BIT]
        if not bloco: break
        
        # faz a média do bloco
        media = sum(bloco) / len(bloco)
        
        # se a média for positiva é 1 senão é 0
        if media > 0:
            bits.append(1)
        else:
            bits.append(0)
    return bits
 
# Decodificação Manchester: Verifica a transição no meio do bit, Alto -> Baixo = 1, Baixo -> Alto = 0
def _decodificar_manchester(sinal: list[float]) -> list[int]:
    # resultado
    bits = []
    # metade das amostras por bit
    meio = AMOSTRAS_POR_BIT // 2

    # percorre o sinal em blocos de AMOSTRAS_POR_BIT
    for i in range(0, len(sinal), AMOSTRAS_POR_BIT):
        bloco = sinal[i : i + AMOSTRAS_POR_BIT]
        if len(bloco) < AMOSTRAS_POR_BIT: break

        # Calcula a média da primeira metade e da segunda metade do bit
        media_primeira_metade = sum(bloco[:meio]) / meio
        media_segunda_metade = sum(bloco[meio:]) / meio
        
        # Se começou alto e terminou baixo -> 1
        if media_primeira_metade > media_segunda_metade:
            bits.append(1)
        else:
            bits.append(0)
    return bits

# Decodificação Bipolar: Nível próximo de 0V -> 0, Nível positivo ou negativo significativo -> 1
def _decodificar_bipolar(sinal: list[float]) -> list[int]:
    # resultado
    bits = []
    # limiar para decidir se é 0 ou 1 (0.5V é seguro se o sinal for +/- 1.0V)
    limiar = VOLTAGEM / 2 

    # percorre o sinal em blocos de AMOSTRAS_POR_BIT
    for i in range(0, len(sinal), AMOSTRAS_POR_BIT):
        bloco = sinal[i : i + AMOSTRAS_POR_BIT]
        if not bloco: break

        # calcula a média absoluta do bloco
        media_absoluta = abs(sum(bloco) / len(bloco))
        
        # se é maior que o limiar é 1 senão é 0
        if media_absoluta > limiar:
            bits.append(1)
        else:
            bits.append(0)
    return bits

################################################ Modulação por portadora ##############################################

# Constantes para Modulação por Portadora
PORTADORA_FREQ = definicoes.PORTADORA_FREQ   # Hz (frequência base da portadora)
AMPLITUDE_MAX = definicoes.AMPLITUDE         # Volts

# recebe uma lista de bits e o tipo de modulação, retorna a lista de amostras do sinal modulado
def modular_portadora(bits: list[int], tipo: str) -> list[float]:
    tipo = tipo.upper()
    if tipo == 'ASK':
        return _modular_ask(bits)
    elif tipo == 'FSK':
        return _modular_fsk(bits)
    elif tipo == 'BPSK': 
        return _modular_bpsk(bits)
    elif tipo == 'QPSK':
        return _modular_qpsk(bits)
    elif tipo == '8PSK': 
        return _modular_8psk(bits)
    elif tipo == '16-QAM':
        return _modular_16qam(bits)
    else:
        raise ValueError(f"Modulação desconhecida: {tipo}")
    
# Modulação ASK: Bit 1 -> Onda senoidal com amplitude A, Bit 0 -> Amplitude 0
def _modular_ask(bits: list[int]) -> list[float]:
    sinal = []
    for bit in bits:
        amp = AMPLITUDE_MAX if bit == 1 else 0.0
        for i in range(AMOSTRAS_POR_BIT):
            t = i / AMOSTRAS_POR_BIT
            sinal.append(amp * math.sin(2 * math.pi * PORTADORA_FREQ * t))
    return sinal

# Modulação FSK: Bit 1 -> Frequência alta, Bit 0 -> Frequência baixa
def _modular_fsk(bits: list[int]) -> list[float]:   
    sinal = []
    f1 = PORTADORA_FREQ * 2
    f2 = PORTADORA_FREQ
    for bit in bits:
        freq = f1 if bit == 1 else f2
        for i in range(AMOSTRAS_POR_BIT):
            t = i / AMOSTRAS_POR_BIT
            sinal.append(AMPLITUDE_MAX * math.sin(2 * math.pi * freq * t))
    return sinal    

# Agrupa bits em tuplas de tamanho_grupo
def _agrupar_bits(bits: list[int], tamanho_grupo: int) -> list[tuple]:
    # resultado
    grupos = []
    for i in range(0, len(bits), tamanho_grupo):
        grupo = tuple(bits[i:i+tamanho_grupo])
        # Preenche com 0 se faltar bits no último grupo (padding)
        if len(grupo) < tamanho_grupo:
             grupo = grupo + (0,) * (tamanho_grupo - len(grupo))
        grupos.append(grupo)
    return grupos

# recebe os bits, o número de bits por símbolo e uma tabela de mapeamento com amplitude e fase e retorna o sinal modulado
def _modular_generico_tabela(bits: list[int], bits_por_simbolo: int, tabela: dict) -> list[float]:
    sinal = []
    grupos = _agrupar_bits(bits, bits_por_simbolo)
    
    for grupo in grupos:
        amp_fator, fase_graus = tabela.get(grupo, (1.0, 0.0))
        fase_rad = math.radians(fase_graus)
        amplitude_final = AMPLITUDE_MAX * amp_fator
        
        for i in range(AMOSTRAS_POR_BIT):
            t = i / AMOSTRAS_POR_BIT
            # CORREÇÃO: Usar math.cos para alinhar fase 0 com eixo X
            amostra = amplitude_final * math.cos(2 * math.pi * PORTADORA_FREQ * t + fase_rad)
            sinal.append(amostra)
            
    return sinal

# Modulação BPSK: Bit 0 -> 0 graus, Bit 1 -> 180 graus
def _modular_bpsk(bits: list[int]) -> list[float]:
    # Baseado no Slide CF-12
    # Bit 0 -> 0 graus
    # Bit 1 -> 180 graus
    # Amplitude é sempre 1.0 (constante)
    tabela_bpsk = {
        (0,): (1.0, 0),
        (1,): (1.0, 180)
    }
    return _modular_generico_tabela(bits, 1, tabela_bpsk)

# Modulação QPSK: Mapeamento padrão de 2 bits por símbolo
def _modular_qpsk(bits: list[int]) -> list[float]:
    # Baseado no Slide CF-12, Pág 29
    # Mapeamento de fase padrão
    tabela_qpsk = {
        (1, 1): (1.0, 45),
        (1, 0): (1.0, 135),
        (0, 0): (1.0, 225),
        (0, 1): (1.0, 315)
    }
    return _modular_generico_tabela(bits, 2, tabela_qpsk)

# Modulação 8PSK: Mapeamento padrão de 3 bits por símbolo
def _modular_8psk(bits: list[int]) -> list[float]:
    # Baseado no Slide CF-12, Pág 41 (Diagrama Visual)
    # Amplitude 1.0 constante
    tabela_8psk = {
        (0, 0, 0): (1.0, 0),
        (0, 0, 1): (1.0, 45),
        (1, 0, 1): (1.0, 90),
        (1, 1, 1): (1.0, 135),
        (0, 1, 1): (1.0, 180),
        (0, 1, 0): (1.0, 225),
        (1, 1, 0): (1.0, 270),
        (1, 0, 0): (1.0, 315)
    }
    return _modular_generico_tabela(bits, 3, tabela_8psk)

# Modulação 16-QAM: Mapeamento padrão de 4 bits por símbolo
def _modular_16qam(bits: list[int]) -> list[float]:
    tabela_16qam = {
        # Quadribit : (Amplitude, Fase)
        (0, 0, 0, 0): (0.33, 225),
        (0, 0, 0, 1): (0.75, 255),
        (0, 0, 1, 0): (0.75, 195),
        (0, 0, 1, 1): (1.00, 225),
        (0, 1, 0, 0): (0.33, 135),
        (0, 1, 0, 1): (0.75, 105),
        (0, 1, 1, 0): (0.75, 165),
        (0, 1, 1, 1): (1.00, 135),
        (1, 0, 0, 0): (0.33, 315),
        (1, 0, 0, 1): (0.75, 285),
        (1, 0, 1, 0): (0.75, 345),
        (1, 0, 1, 1): (1.00, 315),
        (1, 1, 0, 0): (0.33, 45),
        (1, 1, 0, 1): (0.75, 75),
        (1, 1, 1, 0): (0.75, 15),
        (1, 1, 1, 1): (1.00, 45)
    }
    return _modular_generico_tabela(bits, 4, tabela_16qam)

################################################ Demodulação por portadora ##############################################

# recebe o sinal amostrado e o tipo de modulação, retorna a lista de bits recuperados
def demodular_portadora(sinal_amostrado: list[float], tipo: str) -> list[int]:

    # transforma em maiúsculas
    tipo = tipo.upper()
    
    # descobre o tipo e chama a função correta
    if tipo == 'ASK':
        return _demodular_ask(sinal_amostrado)
    elif tipo == 'FSK':
        return _demodular_fsk(sinal_amostrado)
    elif tipo == 'BPSK':
        # BPSK é 1 bit por símbolo 
        tabela_bpsk = {
            (0,): (1.0, 0), 
            (1,): (1.0, 180)}
        return _demodular_generico_tabela(sinal_amostrado, 1, tabela_bpsk)
    elif tipo == 'QPSK':
        # QPSK é 2 bits por símbolo
        tabela_qpsk = {
            (1, 1): (1.0, 45), (1, 0): (1.0, 135),
            (0, 0): (1.0, 225), (0, 1): (1.0, 315)
        }
        return _demodular_generico_tabela(sinal_amostrado, 2, tabela_qpsk)
    elif tipo == '8PSK':
        # 8PSK é 3 bits por símbolo
        tabela_8psk = {
            (0, 0, 0): (1.0, 0), (0, 0, 1): (1.0, 45),
            (1, 0, 1): (1.0, 90), (1, 1, 1): (1.0, 135),
            (0, 1, 1): (1.0, 180), (0, 1, 0): (1.0, 225),
            (1, 1, 0): (1.0, 270), (1, 0, 0): (1.0, 315)
        }
        return _demodular_generico_tabela(sinal_amostrado, 3, tabela_8psk)
    elif tipo == '16-QAM':
        # 16-QAM é 4 bits por símbolo
        tabela_16qam = {
             (0, 0, 0, 0): (0.33, 225), (0, 0, 0, 1): (0.75, 255),
             (0, 0, 1, 0): (0.75, 195), (0, 0, 1, 1): (1.00, 225),
             (0, 1, 0, 0): (0.33, 135), (0, 1, 0, 1): (0.75, 105),
             (0, 1, 1, 0): (0.75, 165), (0, 1, 1, 1): (1.00, 135),
             (1, 0, 0, 0): (0.33, 315), (1, 0, 0, 1): (0.75, 285),
             (1, 0, 1, 0): (0.75, 345), (1, 0, 1, 1): (1.00, 315),
             (1, 1, 0, 0): (0.33, 45),  (1, 1, 0, 1): (0.75, 75),
             (1, 1, 1, 0): (0.75, 15),  (1, 1, 1, 1): (1.00, 45)
        }
        return _demodular_generico_tabela(sinal_amostrado, 4, tabela_16qam)
    else:
        raise ValueError(f"Demodulação desconhecida: {tipo}")

# Demodulação ASK: Calcula a energia do sinal para decidir entre 0 e 1
def _demodular_ask(sinal: list[float]) -> list[int]:
    bits = []
    # Percorre o sinal em blocos de 100 amostras (1 bit)
    for i in range(0, len(sinal), AMOSTRAS_POR_BIT):
        chunk = sinal[i : i + AMOSTRAS_POR_BIT]
        if len(chunk) < AMOSTRAS_POR_BIT: break
        
        # Calcula amplitude média absoluta
        energia = sum([abs(x) for x in chunk]) / len(chunk)
        
        # Limiar de decisão: Metade da amplitude máxima (0.5 * 2/pi aprox para senoide)
        # Ajuste empírico: 0.3 funciona bem para distinguir ruído de sinal
        limiar = 0.3 
        
        bits.append(1 if energia > limiar else 0)
    return bits

def _demodular_fsk(sinal: list[float]) -> list[int]:
    """
    Demodula FSK usando Correlação.
    Compara o sinal recebido com as duas frequências esperadas (f1 e f2).
    Vê qual "casa" melhor.
    """
    bits = []
    f1 = PORTADORA_FREQ * 2 # Frequência do bit 1
    f2 = PORTADORA_FREQ     # Frequência do bit 0
    
    for i in range(0, len(sinal), AMOSTRAS_POR_BIT):
        chunk = sinal[i : i + AMOSTRAS_POR_BIT]
        if len(chunk) < AMOSTRAS_POR_BIT: break
        
        correlacao_f1 = 0
        correlacao_f2 = 0
        
        for j in range(len(chunk)):
            t = j / AMOSTRAS_POR_BIT
            # Multiplica sinal recebido pela onda de referência f1
            correlacao_f1 += chunk[j] * math.sin(2 * math.pi * f1 * t)
            # Multiplica sinal recebido pela onda de referência f2
            correlacao_f2 += chunk[j] * math.sin(2 * math.pi * f2 * t)
            
        # Quem tiver maior correlação ganha (usamos abs para ignorar fase inicial por enquanto)
        if abs(correlacao_f1) > abs(correlacao_f2):
            bits.append(1)
        else:
            bits.append(0)
    return bits

def _demodular_generico_tabela(sinal: list[float], bits_por_simbolo: int, tabela: dict) -> list[int]:
    """
    Demodulador Genérico para PSK e QAM.
    1. Extrai Amplitude e Fase do símbolo recebido.
    2. Compara com a tabela ideal.
    3. Escolhe a opção mais próxima (Menor Distância Euclidiana).
    """
    bits_recuperados = []
    
    for i in range(0, len(sinal), AMOSTRAS_POR_BIT):
        chunk = sinal[i : i + AMOSTRAS_POR_BIT]
        if len(chunk) < AMOSTRAS_POR_BIT: break
        
        # Passo 1: Extrair Componentes I (Cosseno) e Q (Seno) do sinal recebido
        # Isso é matemática de Transformada de Fourier
        soma_i = 0
        soma_q = 0
        for j in range(len(chunk)):
            t = j / AMOSTRAS_POR_BIT
            # Projeção I (In-Phase): Correlaciona com COS
            soma_i += chunk[j] * math.cos(2 * math.pi * PORTADORA_FREQ * t)
            
            # CORREÇÃO PROJEÇÃO Q (Quadrature): Correlaciona com -SIN
            # Isso garante que atan2(Q, I) devolva o ângulo correto
            soma_q += chunk[j] * -1 * math.sin(2 * math.pi * PORTADORA_FREQ * t)
        
        # Normaliza para recuperar a amplitude original (fator 2/N devido à integral de seno^2)
        amp_medida = (2 / AMOSTRAS_POR_BIT) * math.sqrt(soma_i**2 + soma_q**2)
        
        # Calcula a fase em graus (atan2 retorna radianos entre -pi e pi)
        fase_rad = math.atan2(soma_q, soma_i) # Atenção: atan2(y, x) -> (seno, cosseno)
        fase_graus_medida = math.degrees(fase_rad)
        if fase_graus_medida < 0: fase_graus_medida += 360
        
        # Passo 2 e 3: Encontrar na tabela qual tupla de bits tem a menor distância
        # para a (Amplitude, Fase) que acabamos de medir.
        
        melhor_grupo = None
        menor_distancia = float('inf')
        
        for grupo_bits, (amp_ref, fase_ref) in tabela.items():
            # Converter referência polar para retangular (x, y) para calcular distância real
            # Referência
            ref_rad = math.radians(fase_ref)
            x_ref = amp_ref * math.cos(ref_rad)
            y_ref = amp_ref * math.sin(ref_rad)
            
            # Medido
            meas_rad = math.radians(fase_graus_medida)
            x_meas = amp_medida * math.cos(meas_rad)
            y_meas = amp_medida * math.sin(meas_rad)
            
            # Distância Euclidiana
            dist = math.sqrt((x_ref - x_meas)**2 + (y_ref - y_meas)**2)
            
            if dist < menor_distancia:
                menor_distancia = dist
                melhor_grupo = grupo_bits
        
        # Adiciona os bits encontrados à lista final
        if melhor_grupo:
            bits_recuperados.extend(melhor_grupo)
            
    return bits_recuperados

# ... (Mantenha todo o código anterior de imports e modulações digitais)

################################################### Modulação Analógica (Sinal -> Portadora) ###########################

def modular_sinal_analogico(sinal_bb: list[float], tipo_modulacao_bb: str, tipo_portadora: str) -> list[float]:
    """
    Recebe um SINAL DE BANDA BASE (tensões) e o modula em uma portadora.
    """
    tipo_portadora = tipo_portadora.upper()
    sinal_modulado = []
    
    # Caso 1: Modulação ASK (Amplitude Shift Keying)
    # Correção: Para garantir o efeito visual "Liga/Desliga", ignoramos voltagens negativas.
    if tipo_portadora == 'ASK':
        for i, voltagem in enumerate(sinal_bb):
            t = i / AMOSTRAS_POR_BIT
            # Se voltagem > 0 mantém, se for negativa/zero vira 0.0 (Silêncio)
            amplitude = voltagem if voltagem > 0 else 0.0
            val = amplitude * math.sin(2 * math.pi * PORTADORA_FREQ * t)
            sinal_modulado.append(val)
        return sinal_modulado

    # Caso 2: Modulação BPSK (Binary Phase Shift Keying)
    # Aqui a voltagem negativa DEVE inverter a fase (multiplicação direta)
    elif tipo_portadora == 'BPSK':
        for i, voltagem in enumerate(sinal_bb):
            t = i / AMOSTRAS_POR_BIT
            # Multiplicação direta: +V vira seno, -V vira -seno (fase oposta)
            val = voltagem * math.sin(2 * math.pi * PORTADORA_FREQ * t)
            sinal_modulado.append(val)
        return sinal_modulado

    # Caso 3: Modulações Complexas (FSK, QPSK, QAM)
    # Usa a lógica de símbolos
    else:
        bits_temp = decodificar_banda_base(sinal_bb, tipo_modulacao_bb)
        return modular_portadora(bits_temp, tipo_portadora)

################################################### Demodulação Analógica (Portadora -> Sinal) #########################

def demodular_sinal_analogico(sinal_modulado: list[float], tipo_modulacao_bb: str, tipo_portadora: str) -> list[float]:
    """
    Recebe um SINAL MODULADO e recupera o SINAL DE BANDA BASE (Tensão).
    """
    tipo_portadora = tipo_portadora.upper()
    
    # Caso 1: Modulações Lineares (ASK, BPSK)
    if tipo_portadora in ['ASK', 'BPSK']:
        sinal_recuperado = []
        
        # 1. Multiplicação pela Portadora (Mixer Síncrono)
        for i, amostra in enumerate(sinal_modulado):
            t = i / AMOSTRAS_POR_BIT
            # Síncrono: sinal * sen(wt)
            val = amostra * math.sin(2 * math.pi * PORTADORA_FREQ * t)
            sinal_recuperado.append(val * 2) 
            
        # 2. Filtro Passa-Baixa (Média Móvel)
        janela = int(AMOSTRAS_POR_BIT / 2)
        sinal_filtrado = []
        tam = len(sinal_recuperado)
        for i in range(tam):
            inicio = max(0, i - janela)
            fim = min(tam, i + janela)
            media = sum(sinal_recuperado[inicio:fim]) / (fim - inicio)
            sinal_filtrado.append(media)
            
        # 3. REGENERAÇÃO DE SINAL (DECISOR) - CORREÇÃO DO ERRO
        # O NRZ-Polar precisa de +V e -V. O ASK devolve +V e 0V.
        # Vamos forçar o sinal para +1.0 ou -1.0 baseados num limiar.
        sinal_final = []
        limiar = 0.5 # Metade da amplitude
        
        # Detecta se precisamos regenerar para polar (Bipolar/NRZ-Polar) ou manter 0 (Unipolar)
        # Assumiremos regeneração para polar (-1 a 1) para garantir robustez no ASK
        for amostra in sinal_filtrado:
            if tipo_portadora == 'ASK':
                # No ASK: Energia (>0.5) é bit 1 (+V), Sem Energia (<0.5) é bit 0 (-V para NRZ-Polar)
                if amostra > limiar:
                    sinal_final.append(1.0)
                else:
                    sinal_final.append(-1.0) # Força o -1V para o decodificador NRZ funcionar bem
            else:
                # No BPSK: O sinal já vem positivo e negativo naturalmente, apenas repassa (ou limpa ruído)
                sinal_final.append(amostra)
                
        return sinal_final

    # Caso 2: Modulações Complexas (FSK, QPSK, QAM)
    else:
        bits_recuperados = demodular_portadora(sinal_modulado, tipo_portadora)
        return codificar_banda_base(bits_recuperados, tipo_modulacao_bb)