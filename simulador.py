import threading
import time
import random
import camada_fisica
import camada_enlace
import definicoes

class Simulador:
    def __init__(self):
        # Configurações Padrão
        self.tipo_modulacao_bb = "NRZ-POLAR"
        self.tipo_modulacao_portadora = "ASK"
        self.usa_portadora = True
        
        self.tipo_enquadramento = "Contagem de Caracteres"
        self.tipo_erro = "Nenhum" 
        self.snr_ruido = 0.0 
        
        # Armazenamento para Gráficos
        self.sinal_banda_base_tx = [] 
        self.sinal_transmitido = []   
        self.sinal_recebido = []      
        self.sinal_demodulado = []    
        
        self.callback_rx = None

    def configurar(self, mod_bb, mod_portadora, usa_portadora, enquadramento, erro, ruido):
        self.tipo_modulacao_bb = mod_bb
        self.tipo_modulacao_portadora = mod_portadora
        self.usa_portadora = usa_portadora
        self.tipo_enquadramento = enquadramento
        self.tipo_erro = erro
        self.snr_ruido = ruido

    def registrar_callback(self, funcao):
        self.callback_rx = funcao

    def transmitir(self, mensagem_texto: str):
        # Limpa buffers antigos
        self.sinal_transmitido = []
        self.sinal_recebido = []
        
        # Inicia Thread
        thread_tx = threading.Thread(target=self._fluxo_tx, args=(mensagem_texto,))
        thread_tx.start()

    #########################################################################
    # FLUXO DE TRANSMISSÃO (TX)
    #########################################################################
    def _fluxo_tx(self, texto: str):
        print(f"\n[Simulador] TX Iniciado: '{texto}'")
        
        # 1. Aplicação: Texto -> Bits
        bits_dados = self._texto_para_bits(texto)
        
        # 2. Enlace: Controle de Erro + Enquadramento
        bits_ctrl = self._aplicar_controle_erro_tx(bits_dados)
        bits_quadro = self._aplicar_enquadramento_tx(bits_ctrl)
        
        # 3. Física: Codificação Banda Base (Bits -> Tensão)
        sinal_bb = camada_fisica.codificar_banda_base(bits_quadro, self.tipo_modulacao_bb)
        self.sinal_banda_base_tx = sinal_bb 
        
        # 4. Física: Modulação Analógica (Tensão -> Portadora)
        if self.usa_portadora:
            # AGORA CHAMAMOS A CAMADA FÍSICA DIRETAMENTE
            sinal_final = camada_fisica.modular_sinal_analogico(sinal_bb, self.tipo_modulacao_bb, self.tipo_modulacao_portadora)
        else:
            sinal_final = sinal_bb

        self.sinal_transmitido = sinal_final
        
        # 5. Meio de Comunicação (Ruído + Delay)
        sinal_ruidoso = self._aplicar_ruido(sinal_final)
        self.sinal_recebido = sinal_ruidoso
        
        time.sleep(0.5) # Simula propagação
        
        # Passa para o RX
        self._fluxo_rx(sinal_ruidoso)

    #########################################################################
    # FLUXO DE RECEPÇÃO (RX)
    #########################################################################
    def _fluxo_rx(self, sinal_recebido: list[float]):
        print("[Simulador] RX Iniciado...")
        
        # 1. Física: Demodulação Analógica (Portadora -> Tensão)
        if self.usa_portadora:
            # AGORA CHAMAMOS A CAMADA FÍSICA DIRETAMENTE
            sinal_recuperado_bb = camada_fisica.demodular_sinal_analogico(sinal_recebido, self.tipo_modulacao_bb, self.tipo_modulacao_portadora)
        else:
            sinal_recuperado_bb = sinal_recebido
            
        self.sinal_demodulado = sinal_recuperado_bb
        
        # 2. Física: Decodificação Banda Base (Tensão -> Bits)
        bits_brutos = camada_fisica.decodificar_banda_base(sinal_recuperado_bb, self.tipo_modulacao_bb)

        # 3. Enlace: Desenquadramento
        bits_desenquadrados = self._aplicar_enquadramento_rx(bits_brutos)
        
        # 4. Enlace: Verificação de Erros
        bits_finais, status = self._aplicar_controle_erro_rx(bits_desenquadrados)
        
        # 5. Aplicação: Bits -> Texto
        texto = self._bits_para_texto(bits_finais)
        print(f"[RX] Texto Final: {texto} ({status})")
        
        if self.callback_rx:
            self.callback_rx(texto, status)

    # ---------------- MÉTODOS AUXILIARES ----------------
    
    def _texto_para_bits(self, texto: str) -> list[int]:
        bits = []
        for char in texto:
            bin_val = format(ord(char), '08b')
            bits.extend([int(b) for b in bin_val])
        return bits

    def _bits_para_texto(self, bits: list[int]) -> str:
        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8: break
            str_byte = "".join(str(b) for b in byte)
            chars.append(chr(int(str_byte, 2)))
        return "".join(chars)

    def _aplicar_enquadramento_tx(self, bits: list[int]) -> list[int]:
        tipo = self.tipo_enquadramento.upper()
        if tipo.startswith("CONTAGEM"):
            return camada_enlace.enquadrar_contagem_de_caracteres(bits)
        elif "BYTE" in tipo:
            return camada_enlace.enquadrar_insercao_de_bytes(bits)
        elif "BIT" in tipo:
            return camada_enlace.enquadrar_insercao_de_bits(bits)
        return bits 

    def _aplicar_enquadramento_rx(self, bits: list[int]) -> list[int]:
        tipo = self.tipo_enquadramento.upper()
        if tipo.startswith("CONTAGEM"):
            return camada_enlace.desenquadrar_contagem_de_caracteres(bits)
        elif "BYTE" in tipo:
            return camada_enlace.desenquadrar_insercao_de_bytes(bits)
        elif "BIT" in tipo:
            return camada_enlace.desenquadrar_insercao_de_bits(bits)
        return bits

    def _aplicar_controle_erro_tx(self, bits: list[int]) -> list[int]:
        tipo = self.tipo_erro.upper()
        if "PARIDADE" in tipo:
            return camada_enlace.adicionar_paridade_par(bits)
        elif "CHECKSUM" in tipo:
            return camada_enlace.adicionar_checksum(bits)
        elif "CRC" in tipo:
            return camada_enlace.adicionar_crc(bits)
        elif "HAMMING" in tipo:
            return camada_enlace.adicionar_hamming(bits)
        return bits

    def _aplicar_controle_erro_rx(self, bits: list[int]) -> tuple[list[int], str]:
        tipo = self.tipo_erro.upper()
        if "PARIDADE" in tipo:
            ok = camada_enlace.verificar_paridade_par(bits)
            return bits[:-1], ("Sucesso" if ok else "Erro Paridade")
        elif "CHECKSUM" in tipo:
            ok = camada_enlace.verificar_checksum(bits)
            return bits[:-16], ("Sucesso" if ok else "Erro Checksum")
        elif "CRC" in tipo:
            ok = camada_enlace.verificar_crc(bits)
            return bits[:-32], ("Sucesso" if ok else "Erro CRC")
        elif "HAMMING" in tipo:
            dados = camada_enlace.decodificar_hamming(list(bits)) 
            return dados, "Hamming OK"
        return bits, "Sem Verificação"

    def _aplicar_ruido(self, sinal: list[float]) -> list[float]:
        sigma = self.snr_ruido
        if sigma <= 0: return sinal
        return [x + random.gauss(0.0, sigma) for x in sinal]