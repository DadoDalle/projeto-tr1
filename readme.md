Com certeza. Aqui está o conteúdo **completo** do arquivo `README.md`, formatado dentro de um bloco de código único para você copiar e colar sem perder nada.

````markdown
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

Devido à dependência da biblioteca gráfica **GTK 3**, este projeto requer o ambiente **MSYS2** no Windows para gerenciar as dependências nativas. Siga os passos abaixo rigorosamente.

### Passo 1: Instalar o MSYS2
1. Baixe o instalador em [msys2.org](https://www.msys2.org/).
2. Instale no diretório padrão (`C:\msys64`).
3. Ao finalizar, abra o terminal **MSYS2 MinGW 64-bit**.
4. Atualize os pacotes do sistema rodando o comando:
   ```bash
   pacman -Syu
````

*(Se o terminal solicitar fechamento, feche-o e abra novamente para continuar).*

### Passo 2: Instalar Dependências (GTK3, Python, Matplotlib)

No terminal do MSYS2, copie e cole o comando abaixo para instalar tudo de uma vez:

```bash
pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python mingw-w64-x86_64-python-gobject mingw-w64-x86_64-python-matplotlib
```

*Digite `Y` e dê Enter para confirmar a instalação.*

### Passo 3: Configurar Variáveis de Ambiente (PATH)

Para rodar o projeto pelo VSCode ou CMD, o Windows precisa encontrar as bibliotecas instaladas no MSYS2.

1.  No Windows, pesquise por **"Editar as variáveis de ambiente do sistema"**.
2.  Clique no botão **"Variáveis de Ambiente..."**.
3.  Na seção inferior (**Variáveis do sistema**), selecione a variável `Path` e clique em **Editar**.
4.  Clique em **Novo** e adicione exatamente este caminho:
    ```
    C:\msys64\mingw64\bin
    ```
5.  Clique em **OK** em todas as janelas para salvar.

### Passo 4: Executar o Simulador

1.  Abra seu terminal de preferência (VSCode, PowerShell ou CMD).
2.  Navegue até a pasta do projeto.
3.  Execute o comando:

<!-- end list -->

```bash
python interface_gui.py
```

> **Nota Importante:** Certifique-se de que o comando `python` está chamando o Python do MSYS2. Se tiver dúvidas ou erros, use o caminho absoluto:
> `C:\msys64\mingw64\bin\python.exe interface_gui.py`

-----

## 🐧 Guia de Instalação e Execução (Linux)

No Linux (Ubuntu/Debian), a instalação é nativa via apt.

1.  Instale as dependências do sistema:

    ```bash
    sudo apt update
    sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-matplotlib
    ```

2.  Execute o projeto:

    ```bash
    python3 interface_gui.py
    ```

-----

## 🛠️ Estrutura do Projeto

  * `interface_gui.py`: Interface principal (GTK), gerencia entradas, configurações e plotagem dos gráficos.
  * `simulador.py`: Núcleo da simulação. Controla threads de TX/RX, integra as camadas e aplica ruído.
  * `camada_fisica.py`: Implementação matemática das modulações digitais e analógicas.
  * `camada_enlace.py`: Algoritmos de enquadramento, CRC, Checksum e Hamming.
  * `definicoes.py`: Constantes globais (Frequência da portadora, Taxa de amostragem).
  * `main.py`: Arquivo auxiliar para testes unitários de funções isoladas.

-----

## ❓ Solução de Problemas Comuns

**Erro: `ModuleNotFoundError: No module named 'gi'`**

  * **Causa:** Ocorre quando você tenta rodar o código com o Python padrão do Windows em vez do Python do MSYS2 (que possui o GTK instalado).
  * **Solução:** Use o comando completo apontando para o executável correto: `C:\msys64\mingw64\bin\python.exe interface_gui.py`.

**Erro: `Type Error: NavigationToolbar...`**

  * **Causa:** Incompatibilidade com versões mais recentes do Matplotlib.
  * **Solução:** Certifique-se de que está usando o código atualizado do repositório, onde a chamada da Toolbar foi corrigida para `NavigationToolbar(self.canvas)`.

-----

## 👨‍💻 Autores

  * **Grupo de TR1**
  * Disciplina de Telefonia e Redes 1
  * Universidade de Brasília (UnB)

<!-- end list -->

```
```