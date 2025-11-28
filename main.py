import camada_fisica
import camada_enlace

lista1 = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
lista2 = [0, 1, 0, 1]
lista3 = [0, 1, 0, 1, 0, 1]
lista4 = [0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0]
lista = lista4
print("Lista de bits: ", lista)

print("############## MODULAÇÕES DIGITAIS ##############")
print("Modulação NRZ-POLAR: ")
nrzp = camada_fisica.codificar_banda_base(lista, "NRZ-POLAR")
print(nrzp)

print("Modulação MANCHESTER: ")
manchester = camada_fisica.codificar_banda_base(lista, "manchester")
print(manchester)

print("Modulação BIPOLAR: ")
bipolar = camada_fisica.codificar_banda_base(lista, "bipolar")
print(bipolar)

print("############## MODULAÇÕES POR PORTADORA ##############")
print("Modulação ASK: ")
ask = camada_fisica.modular_portadora(lista, "ASK")
print(ask)

print("Modulação FSK: ")
fsk = camada_fisica.modular_portadora(lista, "FSK")
print(fsk)

print("Modulação QPSK: ")
qpsk = camada_fisica.modular_portadora(lista, "QPSK")
print(qpsk)

print("Modulação 8PSK: ")
psk8 = camada_fisica.modular_portadora(lista, "8PSK")
print(psk8)

print("Modulação 16-QAM: ")
qam16 = camada_fisica.modular_portadora(lista, "16-QAM")
print(qam16)

print("############## DEMODULAÇÕES ##############")
print("Demodulação NRZ-POLAR: ")
print(camada_fisica.decodificar_banda_base(nrzp, "NRZ-POLAR"))

print("Demodulação MANCHESTER: ")
print(camada_fisica.decodificar_banda_base(manchester, "manchester"))

print("Demodulação BIPOLAR: ")
print(camada_fisica.decodificar_banda_base(bipolar, "bipolar"))

print("Demodulação ASK: ")
print(camada_fisica.demodular_portadora(ask, "ASK"))

print("Demodulação FSK: ")
print(camada_fisica.demodular_portadora(fsk, "FSK"))    

print("Demodulação QPSK: ")
print(camada_fisica.demodular_portadora(qpsk, "QPSK"))

print("Demodulação 8PSK: ")
print(camada_fisica.demodular_portadora(psk8, "8PSK"))  

print("Demodulação 16-QAM: ")
print(camada_fisica.demodular_portadora(qam16, "16-QAM"))

# Simulando uma sequência de bits que poderia ser gerada por texto 'A' e 'B' ou aleatória
# Vamos forçar casos de borda:
# 1. Sequência com 5 uns para testar Bit Stuffing
# 2. Sequência igual à FLAG (01111110) para testar Byte Stuffing

print("############## TESTES DE ENQUADRAMENTO e DESENQUADRAMENTO ##############")

bits_dados = [0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1,0,0,0,0,0,0] 

print(f"Bits Originais ({len(bits_dados)}): {bits_dados}")
print("-" * 50)

# Teste 1: Contagem de Caracteres
print(">>> Teste: Contagem de Caracteres")
quadro_cont = camada_enlace.enquadrar_contagem_de_caracteres(bits_dados)
print(f"Quadro Tx: {quadro_cont}")
recuperado_cont = camada_enlace.desenquadrar_contagem_de_caracteres(quadro_cont)
print(f"Rx Recuperado: {recuperado_cont}")
print(f"Sucesso: {bits_dados == recuperado_cont}")
print("-" * 50)

# Teste 2: Inserção de Bytes
print(">>> Teste: Inserção de Bytes")
quadro_byte = camada_enlace.enquadrar_insercao_de_bytes(bits_dados)
print(f"Quadro Tx: {quadro_byte}")
recuperado_byte = camada_enlace.desenquadrar_insercao_de_bytes(quadro_byte)
print(f"Rx Recuperado: {recuperado_byte}")
print(f"Sucesso: {bits_dados == recuperado_byte}")
print("-" * 50)

# Teste 3: Inserção de Bits
print(">>> Teste: Inserção de Bits")
quadro_bit = camada_enlace.enquadrar_insercao_de_bits(bits_dados)
print(f"Quadro Tx: {quadro_bit}")
recuperado_bit = camada_enlace.desenquadrar_insercao_de_bits(quadro_bit)
print(f"Rx Recuperado: {recuperado_bit}")
print(f"Sucesso: {bits_dados == recuperado_bit}")
print("-" * 50)

import camada_enlace

# Use uma lista múltipla de 8 para evitar confusão com o padding no Byte Stuffing
bits_dados_teste = [0, 1, 0, 0, 0, 0, 0, 1,   # 'A' (65) invertido ou similar
                    0, 1, 1, 0, 0, 0, 1, 0]   # 'b' (98)

print(f"\nBits Originais ({len(bits_dados_teste)}): {bits_dados_teste}")

print("\n--- TESTE DETECÇÃO DE ERROS ---")

# 1. Paridade
print("1. Paridade Par")
tx_paridade = camada_enlace.adicionar_paridade_par(bits_dados_teste)
print(f"Tx (+1 bit): {tx_paridade}")
check_paridade = camada_enlace.verificar_paridade_par(tx_paridade)
print(f"Verificação OK? {check_paridade}")

# Simula Erro
tx_paridade_erro = list(tx_paridade)
tx_paridade_erro[0] = 1 if tx_paridade_erro[0] == 0 else 0 # Inverte o primeiro bit
print(f"Verificação com Erro? {camada_enlace.verificar_paridade_par(tx_paridade_erro)}")


# 2. Checksum
print("\n2. Checksum (16 bits)")
tx_checksum = camada_enlace.adicionar_checksum(bits_dados_teste)
print(f"Tx (+16 bits): {tx_checksum}")
check_checksum = camada_enlace.verificar_checksum(tx_checksum)
print(f"Verificação OK? {check_checksum}")

# 3. CRC-32
print("\n3. CRC-32 (IEEE 802)")
tx_crc = camada_enlace.adicionar_crc(bits_dados_teste)
print(f"Tx (+32 bits): {tx_crc}")
check_crc = camada_enlace.verificar_crc(tx_crc)
print(f"Verificação OK? {check_crc}")

# Simula Erro no CRC
tx_crc_erro = list(tx_crc)
tx_crc_erro[5] = 1 if tx_crc_erro[5] == 0 else 0 # Inverte um bit no meio
print(f"Verificação CRC com Erro? {camada_enlace.verificar_crc(tx_crc_erro)}")

import camada_enlace

# Usamos 8 bits de dados para forçar um Hamming maior (necessita 4 bits de paridade -> total 12 bits)
dados_hamming = [1, 0, 1, 1, 0, 0, 1, 1] 

print("\n--- TESTE CORREÇÃO DE ERROS (HAMMING GENÉRICO) ---")
print(f"Dados originais: {dados_hamming}")

# 1. Codificar
tx_hamming = camada_enlace.adicionar_hamming(dados_hamming)
print(f"Codificado (Tx): {tx_hamming} (Tamanho: {len(tx_hamming)})")

# 2. Simular Erro (Inverter o bit na posição 7, por exemplo)
rx_com_erro = list(tx_hamming)
posicao_erro = 6 # Índice 6 (é a 7ª posição na lógica humana)
rx_com_erro[posicao_erro] = 1 if rx_com_erro[posicao_erro] == 0 else 0
print(f"Recebido c/ Erro:{rx_com_erro}")

# 3. Decodificar e Corrigir
dados_corrigidos = camada_enlace.decodificar_hamming(rx_com_erro)
print(f"Dados Corrigidos: {dados_corrigidos}")

print(f"Sucesso? {dados_hamming == dados_corrigidos}")

import simulador
import time

def callback(msg, status):
    print(f"\n[CALLBACK] Msg: '{msg}' | Status: {status}")

sim = simulador.Simulador()
sim.registrar_callback(callback)

# Teste 1: Manchester (Banda Base) + ASK (Portadora)
# Isso deve gerar uma onda quadrada que liga e desliga a portadora
print("--- Teste: NRZ-POLAR + ASK ---")
sim.configurar(mod_bb="Manchester", 
               mod_portadora="16-QAM", 
               usa_portadora=True,
               enquadramento="Contagem de Caracteres", 
               erro="CRC", 
               ruido=0.0)

sim.transmitir("U") # 'U' é 01010101 (bom para ver transições)
time.sleep(2)


""" Teste de graficos usando plotly
# graficos
import plotly.graph_objects as go
from camada_fisica import AMOSTRAS_POR_BIT # Importe a constante para saber onde desenhar as linhas

def visualizar_sinal(sinal: list[float], titulo: str, bits: list[int]):
    
    #Gera um gráfico interativo do sinal modulado usando Plotly.
    #Marca as divisões dos bits para facilitar a conferência.
    
    # Eixo X (tempo em "períodos de bit")
    x = [i / AMOSTRAS_POR_BIT for i in range(len(sinal))]
    
    fig = go.Figure()

    # Adiciona a onda do sinal
    fig.add_trace(go.Scatter(
        x=x, 
        y=sinal, 
        mode='lines', 
        name='Sinal Modulado',
        line=dict(color='blue', width=2)
    ))

    # Adiciona linhas verticais para separar os bits
    # E anotações com o valor do bit original
    for i, bit in enumerate(bits):
        # Linha vertical
        fig.add_shape(
            type="line",
            x0=i, y0=min(sinal)-0.2, x1=i, y1=max(sinal)+0.2,
            line=dict(color="gray", width=1, dash="dot")
        )
        # Texto do bit no topo
        fig.add_annotation(
            x=i + 0.5, # Centraliza no bit
            y=max(sinal) + 0.1,
            text=str(bit),
            showarrow=False,
            font=dict(size=14, color="red")
        )

    fig.update_layout(
        title=f"Visualização: {titulo}",
        xaxis_title="Tempo (Bits)",
        yaxis_title="Amplitude / Tensão (V)",
        template="plotly_white",
        height=400  # Altura do gráfico
    )
    
    fig.show()

# Lista das modulações que você quer ver
modulacoes = ['NRZ-POLAR', 'MANCHESTER', 'BIPOLAR', 'ASK', 'FSK', 'BPSK', 'QPSK', '8PSK', '16-QAM']

for tipo in modulacoes:
    print(f"--- Testando {tipo} ---")
    
    # 1. Modular
    sinal_modulado = camada_fisica.modular_portadora(lista, tipo) if tipo in ['ASK', 'FSK', 'BPSK', 'QPSK', '8PSK', '16-QAM'] else camada_fisica.codificar_banda_base(lista, tipo)
    
    # 2. Visualizar (Abre o gráfico no navegador)
    visualizar_sinal(sinal_modulado, f"Modulação {tipo}", lista)

"""