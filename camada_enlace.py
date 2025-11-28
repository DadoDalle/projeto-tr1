import camada_fisica

# Vamos assumir que trabalharemos sempre com blocos de 8 bits (Bytes) para os métodos baseados em byte.
# Definições para Byte Stuffing
FLAG_BYTE = [0, 1, 1, 1, 1, 1, 1, 0] # Representação do caractere '~' ou similar
ESC_BYTE  = [0, 0, 0, 1, 1, 0, 1, 1] # Representação do caractere de escape (ESC)

# Definições para Bit Stuffing
FLAG_BIT  = [0, 1, 1, 1, 1, 1, 1, 0] # 0x7E

def dados_para_bytes(bits: list[int]) -> list[list[int]]:
    """Auxiliar: Quebra uma lista de bits em lista de listas (bytes)"""
    bytes_lista = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8: # Preenchimento se sobrar
            byte += [0] * (8 - len(byte))
        bytes_lista.append(byte)
    return bytes_lista

def bytes_para_dados(bytes_lista: list[list[int]]) -> list[int]:
    """Auxiliar: Junta lista de bytes em uma lista plana de bits"""
    bits = []
    for b in bytes_lista:
        bits.extend(b)
    return bits

###########################################################
# 1. Contagem de Caracteres
###########################################################

def enquadrar_contagem_de_caracteres(bits: list[int]) -> list[int]:
    """
    Adiciona um cabeçalho no início indicando quantos bytes existem no quadro.
    O cabeçalho também conta como um byte.
    """
    lista_bytes = dados_para_bytes(bits)
    # Número de bytes de dados + 1 byte de cabeçalho
    tamanho = len(lista_bytes) + 1 
    
    # Converte o tamanho para binário (8 bits)
    header = [int(x) for x in format(tamanho, '08b')]
    
    # Retorna Header + Dados
    return header + bits

def desenquadrar_contagem_de_caracteres(bits: list[int]) -> list[int]:
    """
    Lê o primeiro byte para saber o tamanho e extrai os dados.
    """
    if len(bits) < 8: return []
    
    # Lê o header (primeiros 8 bits)
    header = bits[:8]
    # Converte binário para inteiro manualmente ou com int()
    tamanho_total = int("".join(str(x) for x in header), 2)
    
    # O payload são os bits restantes. 
    # Obs: Em uma simulação real de fluxo contínuo, usaríamos 'tamanho_total' 
    # para saber onde cortar o próximo quadro. Aqui pegamos o restante.
    payload = bits[8 : 8 + (tamanho_total - 1) * 8]
    
    return payload

###########################################################
# 2. Inserção de Bytes (Byte Stuffing)
###########################################################

def enquadrar_insercao_de_bytes(bits: list[int]) -> list[int]:
    """
    Usa uma FLAG no inicio e fim. Se a FLAG ou ESC aparecerem nos dados,
    insere um ESC antes.
    """
    lista_bytes = dados_para_bytes(bits)
    quadro_bytes = []
    
    # Adiciona FLAG de início
    quadro_bytes.append(FLAG_BYTE)
    
    for byte in lista_bytes:
        # Se o byte de dados for igual à FLAG ou igual ao ESC, insere ESC antes
        if byte == FLAG_BYTE or byte == ESC_BYTE:
            quadro_bytes.append(ESC_BYTE)
        quadro_bytes.append(byte)
        
    # Adiciona FLAG de fim
    quadro_bytes.append(FLAG_BYTE)
    
    return bytes_para_dados(quadro_bytes)

def desenquadrar_insercao_de_bytes(bits: list[int]) -> list[int]:
    """
    Remove as FLAGS e trata o caractere de escape (ESC).
    """
    lista_bytes = dados_para_bytes(bits)
    dados_recuperados = []
    
    ignorar_proximo = False # Flag para pular bytes que são apenas delimitadores processados
    escape_ativo = False    # Indica se o byte anterior foi um ESC
    
    # Ignora a primeira FLAG (início) e assume que a última é FLAG (fim)
    # Em um stream real, teríamos que buscar a FLAG.
    conteudo = lista_bytes[1:-1] 
    
    for byte in conteudo:
        if escape_ativo:
            # Se o anterior foi ESC, este byte é dado (mesmo que pareça FLAG ou ESC)
            dados_recuperados.append(byte)
            escape_ativo = False
        else:
            if byte == ESC_BYTE:
                escape_ativo = True # Próximo byte será tratado como dado puro
            elif byte == FLAG_BYTE:
                # Se achou uma flag sem escape no meio, algo deu errado ou é fim de quadro
                continue 
            else:
                dados_recuperados.append(byte)
                
    return bytes_para_dados(dados_recuperados)

###########################################################
# 3. Inserção de Bits (Bit Stuffing)
###########################################################

def enquadrar_insercao_de_bits(bits: list[int]) -> list[int]:
    """
    FLAG: 01111110.
    Sempre que aparecerem cinco '1's seguidos nos dados, insere um '0'.
    """
    quadro = []
    
    # FLAG de Início
    quadro.extend(FLAG_BIT)
    
    contador_uns = 0
    for bit in bits:
        quadro.append(bit)
        if bit == 1:
            contador_uns += 1
            if contador_uns == 5:
                # Inserção do bit 0 (stuffing)
                quadro.append(0)
                contador_uns = 0
        else:
            contador_uns = 0
            
    # FLAG de Fim
    quadro.extend(FLAG_BIT)
    
    return quadro

def desenquadrar_insercao_de_bits(bits: list[int]) -> list[int]:
    """
    Remove as FLAGS e remove o '0' inserido após cinco '1's.
    """
    # Remove as flags (assumindo 8 bits cada nas pontas)
    if len(bits) < 16: return []
    payload_raw = bits[8:-8]
    
    dados = []
    contador_uns = 0
    i = 0
    
    while i < len(payload_raw):
        bit = payload_raw[i]
        
        if bit == 1:
            contador_uns += 1
            dados.append(bit)
            i += 1
        else:
            # Se é zero
            if contador_uns == 5:
                # Este zero foi inserido pelo transmissor (stuffing), ignorar.
                i += 1 
                contador_uns = 0
            else:
                dados.append(bit)
                contador_uns = 0
                i += 1
                
    return dados

###########################################################
# 4. Detecção de Erros: Bit de Paridade Par
###########################################################

def adicionar_paridade_par(bits: list[int]) -> list[int]:
    """
    Adiciona 1 bit ao final. O bit será 1 se o número de '1's for ímpar,
    para tornar o total par.
    """
    qtd_uns = sum(bits)
    paridade = 1 if (qtd_uns % 2 != 0) else 0
    return bits + [paridade]

def verificar_paridade_par(bits: list[int]) -> bool:
    """
    Verifica se a paridade do conjunto (dados + bit paridade) está correta.
    """
    if not bits: return True
    return (sum(bits) % 2) == 0

###########################################################
# 5. Detecção de Erros: Checksum (16 bits)
###########################################################

def _calcular_checksum_16b(bits: list[int]) -> list[int]:
    """
    Algoritmo de Checksum (estilo Internet Checksum - RFC 1071).
    Soma palavras de 16 bits e faz o complemento de 1.
    """
    # 1. Garante que a lista é par (múltiplo de 16 bits para a soma)
    # Se sobrar bits (ex: 8 bits), fazemos padding com zeros à direita para formar a última palavra
    dados = list(bits)
    while len(dados) % 16 != 0:
        dados.append(0)
        
    soma = 0
    # 2. Percorre de 16 em 16 bits
    for i in range(0, len(dados), 16):
        bloco = dados[i:i+16]
        # Converte lista de bits para inteiro
        valor = int("".join(str(b) for b in bloco), 2)
        soma += valor
        
        # 3. Trata o overflow (wrap around) se a soma passar de 16 bits (65535)
        if soma > 0xFFFF:
            soma = (soma & 0xFFFF) + 1
            
    # 4. Complemento de 1 (inverte os bits)
    checksum = ~soma & 0xFFFF
    
    # Retorna como lista de 16 bits
    return [int(x) for x in format(checksum, '016b')]

def adicionar_checksum(bits: list[int]) -> list[int]:
    """
    Calcula o checksum dos dados e anexa ao final (16 bits).
    """
    cks = _calcular_checksum_16b(bits)
    return bits + cks

def verificar_checksum(bits: list[int]) -> bool:
    """
    Recalcula o checksum de todo o quadro (dados + checksum recebido).
    Em lógica de complemento de 1, a soma total deve ser 0 (ou 0xFFFF dependendo da implementação).
    Aqui, vamos separar: recalcula o checksum da parte de dados e compara com o final.
    """
    if len(bits) < 16: return False
    
    dados = bits[:-16]
    checksum_recebido = bits[-16:]
    
    checksum_calculado = _calcular_checksum_16b(dados)
    
    return checksum_calculado == checksum_recebido

###########################################################
# 6. Detecção de Erros: CRC-32 (IEEE 802)
###########################################################

def _calcular_crc32(bits: list[int]) -> list[int]:
    """
    Implementação manual do CRC-32 (IEEE 802.3).
    Polinômio: 0x04C11DB7 (x^32 + x^26 + ... + 1)
    
    Nota: O padrão Ethernet usa:
    1. Valor inicial 0xFFFFFFFF
    2. Processamento bit a bit (geralmente LSB first, mas aqui faremos direto na lógica polinomial)
    3. Inversão final (XOR 0xFFFFFFFF)
    
    Para fins didáticos e compatibilidade com verificadores simples online, 
    vamos implementar a DIVISÃO POLINOMIAL padrão com o polinômio 0x04C11DB7.
    """
    
    # Polinômio gerador IEEE 802.3 (33 bits, o bit mais significativo é implícito na divisão)
    # 1 0000 0100 1100 0001 0001 1101 1011 0111
    poly = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 
            0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1] 

    # Adiciona 32 zeros ao final dos dados (grau do polinômio)
    dados_aumentados = bits + [0]*32
    
    # Converte para uma lista mutável para fazer a divisão (XOR)
    resto = list(dados_aumentados)
    
    for i in range(len(bits)):
        if resto[i] == 1:
            # Faz XOR com o polinômio a partir desta posição
            for j in range(len(poly)):
                resto[i + j] = resto[i + j] ^ poly[j]
                
    # O resto são os últimos 32 bits
    crc = resto[-(len(poly)):] # Pega os últimos 32 bits
    return crc

def adicionar_crc(bits: list[int]) -> list[int]:
    """
    Calcula CRC-32 e anexa ao final.
    """
    crc = _calcular_crc32(bits)
    return bits + crc

def verificar_crc(bits: list[int]) -> bool:
    """
    Verifica se o resto da divisão dos bits recebidos pelo polinômio é zero.
    """
    if len(bits) < 32: return False
    
    # Se a mensagem está correta (Dados + CRC), ao dividir pelo polinômio, o resto deve ser zero.
    # Reutilizamos a função _calcular_crc32 mas passando TUDO.
    # Nota: _calcular_crc32 adiciona 32 zeros. Para verificar, 
    # podemos simplesmente rodar a lógica de divisão nos dados recebidos sem adicionar zeros extras
    # e ver se o final zera.
    
    # Forma alternativa robusta: Separa e compara.
    dados = bits[:-32]
    crc_recebido = bits[-32:]
    crc_calculado = _calcular_crc32(dados)
    
    return crc_recebido == crc_calculado

###########################################################
# 7. Correção de Erros: Hamming (Genérico / Payload Completo)
###########################################################

def adicionar_hamming(bits_dados: list[int]) -> list[int]:
    """
    Implementa Hamming genérico para qualquer tamanho de payload.
    Os bits de paridade são inseridos nas posições que são potências de 2 (1, 2, 4, 8...).
    """
    m = len(bits_dados)
    r = 0
    
    # 1. Calcula quantos bits de paridade (r) são necessários
    # Fórmula: 2^r >= m + r + 1
    while (2**r) < (m + r + 1):
        r += 1
        
    # Tamanho total da mensagem codificada
    tamanho_total = m + r
    
    # 2. Inicializa a lista com zeros (ou None) para preencher depois
    # Usaremos indexação baseada em 1 para a lógica matemática, mas a lista é base 0.
    mensagem = [0] * tamanho_total
    
    # 3. Preenche as posições de DADOS (que NÃO são potências de 2)
    j = 0 # índice para percorrer bits_dados
    for i in range(1, tamanho_total + 1):
        # Se i não é potência de 2, é um bit de dados
        # (i & (i - 1)) == 0 verifica se é potência de 2
        if (i & (i - 1)) != 0: 
            mensagem[i-1] = bits_dados[j]
            j += 1
            
    # 4. Calcula os bits de PARIDADE
    # Para cada bit de paridade na posição 2^x
    for i in range(r):
        posicao_paridade = 2**i # 1, 2, 4, 8...
        
        # O bit de paridade deve garantir que a quantidade de 1s nas posições controladas seja par
        xor_total = 0
        
        # Verifica todos os bits da mensagem
        for k in range(1, tamanho_total + 1):
            # Se o bit k tem o bit 'i' setado na sua representação binária, ele é controlado por esta paridade
            # Ex: Se estamos calculando paridade 2 (0010), olhamos bits 2, 3, 6, 7, 10, 11...
            if k & posicao_paridade:
                # Soma (XOR) apenas os bits que já foram preenchidos (ignorando a própria posição de paridade que estamos calculando)
                if k != posicao_paridade:
                    xor_total ^= mensagem[k-1]
        
        # Define o valor do bit de paridade
        mensagem[posicao_paridade - 1] = xor_total
        
    return mensagem

def decodificar_hamming(bits_recebidos: list[int]) -> list[int]:
    """
    Verifica a paridade, corrige 1 bit de erro (se houver) e remove os bits de redundância.
    Retorna apenas os DADOS originais.
    """
    n = len(bits_recebidos)
    # Precisamos descobrir quantos bits são de paridade (r) com base no tamanho total (n)
    # Sabemos que n = m + r. A relação de hamming bits é logarítmica.
    r = 0
    while (2**r) < (n + 1): # Aproximei a condição
        r += 1
        
    erro_posicao = 0
    
    # 1. Recalcula as paridades para achar a "Síndrome"
    for i in range(r):
        posicao_paridade = 2**i
        xor_total = 0
        
        # Verifica os bits controlados por esta paridade
        for k in range(1, n + 1):
            if k & posicao_paridade:
                xor_total ^= bits_recebidos[k-1]
        
        # Se xor_total for 1, significa que a paridade não bateu (erro detectado)
        # Somamos a posição da paridade ao erro_posicao para descobrir o índice do bit ruim
        if xor_total != 0:
            erro_posicao += posicao_paridade
            
    # 2. Corrige o erro se houver (posicao > 0)
    if erro_posicao > 0:
        print(f"Hamming: Erro detectado e corrigido na posição {erro_posicao}!")
        # Inverte o bit errado (lembrando que erro_posicao é base 1, lista é base 0)
        # Só corrigimos se estiver dentro do range (segurança)
        if erro_posicao <= n:
            bits_recebidos[erro_posicao - 1] ^= 1
            
    # 3. Remove os bits de paridade e extrai os dados
    dados_recuperados = []
    for i in range(1, n + 1):
        # Se não é potência de 2, é dado
        if (i & (i - 1)) != 0:
            dados_recuperados.append(bits_recebidos[i-1])
            
    return dados_recuperados