# Simulador de Camada Física e Enlace - Telefonia e Redes 1

Este projeto é um simulador didático das camadas **Física** e de **Enlace**, desenvolvido para a disciplina de Telefonia e Redes 1. O software permite visualizar o comportamento de sinais digitais e analógicos, aplicando técnicas de modulação, enquadramento, detecção e correção de erros, com visualização gráfica em tempo real.

---

## 📋 Funcionalidades Implementadas

### 1. Camada Física
* **Codificação de Banda Base:**
  * NRZ-Polar
  * Manchester
  * Bipolar
* **Modulação por Portadora:**
  * ASK (Amplitude Shift Keying)
  * FSK (Frequency Shift Keying)
  * BPSK, QPSK, 8PSK (Phase Shift Keying)
  * 16-QAM (Quadrature Amplitude Modulation)
  * **Modo "Nenhuma":** Visualização pura do sinal em banda base.
* **Simulação de Meio:**
  * Inserção de Ruído Branco Gaussiano Aditivo (AWGN) com SNR configurável via slider.

### 2. Camada de Enlace
* **Enquadramento:**
  * Contagem de Caracteres.
  * Inserção de Bytes (Byte Stuffing).
  * Inserção de Bits (Bit Stuffing).
* **Controle de Erros (Detecção):**
  * Bit de Paridade Par.
  * Checksum (16 bits).
  * CRC-32 (IEEE 802).
* **Controle de Erros (Correção):**
  * Código de Hamming.

### 3. Interface Gráfica
* Desenvolvida em **GTK 3** via PyGObject.
* Gráficos interativos (Zoom/Pan) utilizando **Matplotlib**.
* Arquitetura *Multithread* (TX e RX independentes).

---

## 🚀 Guia de Instalação e Execução (Windows)

Devido à dependência da biblioteca gráfica **GTK 3**, este projeto requer o ambiente **MSYS2** no Windows. Siga os passos abaixo rigorosamente.

### Passo 1: Instalar o MSYS2
1. Baixe o instalador em [msys2.org](https://www.msys2.org/).
2. Instale no diretório padrão (`C:\msys64`).
3. Ao finalizar, abra o terminal **MSYS2 MinGW 64-bit**.
4. Atualize os pacotes do sistema rodando o comando:
   ```bash
   pacman -Syu