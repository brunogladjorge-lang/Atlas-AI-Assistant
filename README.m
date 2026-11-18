# 🤖 Atlas & Atenas — Assistente Virtual Desktop com IA

Assistente de desktop desenvolvido em **Python** com processamento de linguagem natural via **Google Gemini API** (`gemini-2.0-flash`), síntese de voz neural, interface gráfica expressiva e automação de sistema operacional.

## ⚙️ Funcionalidades
* **Inteligência Conversacional & Personas:** Integração com a API do Google Gemini com alternância dinâmica entre as personas **Atlas** e **Atenas**.
* **Voz Neural (TTS) & Reconhecimento de Voz:** Escuta ativa via `SpeechRecognition` e voz neural em português brasileiro (`edge-tts`).
* **Interface Visual Expressiva:** Olhos animados em janela sem bordas (`pygame`) com reações visuais em tempo real e suporte a múltiplos monitores.
* **Automação & Rede:** Envio de mensagens/mídia (`pywhatkit`), controle de sistema e monitoramento de conectividade local.

## 🚀 Como Executar
1. Clone este repositório:
   ```bash
   git clone https://github.com/brunogladjorge-lang/Atlas-AI-Assistant.git

2. Instalçao do python.
 - Execute esse comando no seu terminal para instalar as dependencias do projeto
 - pip install google-genai edge-tts pygame SpeechRecognition pywhatkit

3. Insira sua chave da API do Google Gemini na variável CHAVE_API dentro de main.py.

