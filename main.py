import speech_recognition as sr
import pygame
import os
import time
import datetime
import subprocess
from google import genai
import edge_tts
import asyncio
import pywhatkit
import threading
import random
import math
import json


CHAVE_API = "COLOQUE_SUA_CHAVE_AQUI"
client = genai.Client(api_key=CHAVE_API)
NOME_DO_MODELO = 'models/gemini-2.0-flash'

ESTADO_ATUAL = "idle"
PERSONA_ATUAL = "atlas"


def run_eyes_ui():
    global ESTADO_ATUAL, PERSONA_ATUAL
    
    pygame.init()
    
    
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
    
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    pygame.display.set_caption("Atlas Core System")
    clock = pygame.time.Clock()
    
    BLACK = (0, 0, 0)
    
    
    ATLAS_BASE = (0, 255, 255)
    ATLAS_LISTEN = (50, 100, 255)
    ATLAS_THINK = (255, 255, 0)
    
   
    ATENA_BASE = (255, 20, 147)
    ATENA_LISTEN = (255, 105, 180)
    ATENA_THINK = (138, 43, 226)

    
    COLOR_ANGRY = (255, 0, 0)    
    COLOR_SAD = (0, 191, 255)     
    COLOR_HAPPY = (50, 205, 50)   

    eye_base_width = int(SCREEN_WIDTH * 0.18) 
    eye_base_height = int(SCREEN_HEIGHT * 0.40) 
    eye_radius = int(eye_base_width * 0.3) 
    eye_gap = int(SCREEN_WIDTH * 0.1) 
    
    total_face_width = (eye_base_width * 2) + eye_gap
    base_left_x = (SCREEN_WIDTH - total_face_width) // 2
    base_right_x = base_left_x + eye_base_width + eye_gap
    base_y = (SCREEN_HEIGHT - eye_base_height) // 2
    
    MAX_SHIFT_X = int(SCREEN_WIDTH * 0.02)
    MAX_SHIFT_Y = int(SCREEN_HEIGHT * 0.02)
    
    internal_shift_x, internal_shift_y = 0, 0
    target_shift_x, target_shift_y = 0, 0
    move_timer, next_move_time = 0, random.uniform(3, 7)
    interpolation_speed = 5 
    
    running = True
    blink_timer, blink_duration = 0, 0
    next_blink_time = random.uniform(2, 5)

    while running:
        dt = clock.tick(60) / 1000.0 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                ESTADO_ATUAL = "off"
                running = False

        if ESTADO_ATUAL == "off": 
            running = False
            
        screen.fill(BLACK)
        
        if PERSONA_ATUAL == "atlas":
            cor_base, cor_listen, cor_think = ATLAS_BASE, ATLAS_LISTEN, ATLAS_THINK
        else:
            cor_base, cor_listen, cor_think = ATENA_BASE, ATENA_LISTEN, ATENA_THINK

        curr_width, curr_height, curr_color = eye_base_width, eye_base_height, cor_base
        draw_radius = eye_radius
        
        
        if ESTADO_ATUAL == "thinking":
            target_shift_y = -int(MAX_SHIFT_Y * 0.8)
            target_shift_x = int(MAX_SHIFT_X * 0.7)
            interpolation_speed = 10
        elif ESTADO_ATUAL == "idle":
            interpolation_speed = 3 
            move_timer += dt
            if move_timer >= next_move_time:
                target_shift_x = random.randint(-MAX_SHIFT_X, MAX_SHIFT_X)
                target_shift_y = random.randint(-MAX_SHIFT_Y, MAX_SHIFT_Y)
                move_timer, next_move_time = 0, random.uniform(3, 7)
        else: 
            target_shift_x, target_shift_y, interpolation_speed = 0, 0, 7 

        fraction = min(interpolation_speed * dt, 1.0) 
        internal_shift_x += (target_shift_x - internal_shift_x) * fraction
        internal_shift_y += (target_shift_y - internal_shift_y) * fraction
        
        draw_y = base_y + internal_shift_y
        draw_left_x = base_left_x + internal_shift_x
        draw_right_x = base_right_x + internal_shift_x
        
       
        if ESTADO_ATUAL == "listening": 
            curr_color, draw_radius = cor_listen, int(curr_width * 0.5) 
        elif ESTADO_ATUAL == "thinking": 
            curr_color = cor_think
        elif ESTADO_ATUAL == "speaking": 
            curr_color = cor_base 
        elif ESTADO_ATUAL == "angry": 
            curr_color = COLOR_ANGRY
        elif ESTADO_ATUAL == "sad": 
            curr_color = COLOR_SAD
        elif ESTADO_ATUAL == "happy": 
            curr_color = COLOR_HAPPY
            
       
        is_blinking = False
        blink_timer += dt
        if blink_timer >= next_blink_time:
            is_blinking = True
            blink_duration += dt
            if blink_duration >= 0.15: 
                blink_timer, blink_duration, next_blink_time, is_blinking = 0, 0, random.uniform(2, 5), False
        
        y_blink_draw = (SCREEN_HEIGHT // 2) - (int(eye_base_height * 0.05) // 2) if is_blinking else draw_y
            
       
        if not is_blinking:
            if ESTADO_ATUAL == "angry":
                curr_height = int(eye_base_height * 0.50)
                y_blink_draw = (SCREEN_HEIGHT // 2) - (curr_height // 2)
                pygame.draw.polygon(screen, curr_color, [
                    (draw_left_x, y_blink_draw), 
                    (draw_left_x + curr_width, y_blink_draw + (curr_height // 2)), 
                    (draw_left_x + curr_width, y_blink_draw + curr_height + (curr_height // 2)), 
                    (draw_left_x, y_blink_draw + curr_height)
                ])
                pygame.draw.polygon(screen, curr_color, [
                    (draw_right_x, y_blink_draw + (curr_height // 2)), 
                    (draw_right_x + curr_width, y_blink_draw), 
                    (draw_right_x + curr_width, y_blink_draw + curr_height), 
                    (draw_right_x, y_blink_draw + curr_height + (curr_height // 2))
                ])
            elif ESTADO_ATUAL == "sad":
                curr_height = int(eye_base_height * 0.50)
                y_blink_draw = (SCREEN_HEIGHT // 2) - (curr_height // 2)
                pygame.draw.polygon(screen, curr_color, [
                    (draw_left_x, y_blink_draw + (curr_height // 2)), 
                    (draw_left_x + curr_width, y_blink_draw), 
                    (draw_left_x + curr_width, y_blink_draw + curr_height), 
                    (draw_left_x, y_blink_draw + curr_height + (curr_height // 2))
                ])
                pygame.draw.polygon(screen, curr_color, [
                    (draw_right_x, y_blink_draw), 
                    (draw_right_x + curr_width, y_blink_draw + (curr_height // 2)), 
                    (draw_right_x + curr_width, y_blink_draw + curr_height + (curr_height // 2)), 
                    (draw_right_x, y_blink_draw + curr_height)
                ])
            elif ESTADO_ATUAL == "happy":
                curr_height = int(eye_base_height * 0.40)
                y_blink_draw = (SCREEN_HEIGHT // 2) - (curr_height // 2)
                pygame.draw.polygon(screen, curr_color, [
                    (draw_left_x, y_blink_draw + (curr_height // 2)), 
                    (draw_left_x + (curr_width // 2), y_blink_draw), 
                    (draw_left_x + curr_width, y_blink_draw + (curr_height // 2)), 
                    (draw_left_x + (curr_width // 2), y_blink_draw + (curr_height // 4))
                ])
                pygame.draw.polygon(screen, curr_color, [
                    (draw_right_x, y_blink_draw + (curr_height // 2)), 
                    (draw_right_x + (curr_width // 2), y_blink_draw), 
                    (draw_right_x + curr_width, y_blink_draw + (curr_height // 2)), 
                    (draw_right_x + (curr_width // 2), y_blink_draw + (curr_height // 4))
                ])
            else:
                pygame.draw.rect(screen, curr_color, pygame.Rect(draw_left_x, y_blink_draw, curr_width, curr_height), border_radius=draw_radius)
                pygame.draw.rect(screen, curr_color, pygame.Rect(draw_right_x, y_blink_draw, curr_width, curr_height), border_radius=draw_radius)
        else:
            pygame.draw.line(screen, curr_color, (draw_left_x, SCREEN_HEIGHT//2), (draw_left_x + curr_width, SCREEN_HEIGHT//2), 6)
            pygame.draw.line(screen, curr_color, (draw_right_x, SCREEN_HEIGHT//2), (draw_right_x + curr_width, SCREEN_HEIGHT//2), 6)

        pygame.display.flip()
    pygame.quit()


pygame.mixer.init()

def qual_meu_wifi():
    try:
        resultado = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('cp1252', errors="ignore")
        for linha in resultado.split('\n'):
            if "SSID" in linha and "BSSID" not in linha: 
                return linha.split(':')[1].strip()
        return "Desconectado"
    except: 
        return "Desconhecido"

async def gerar_audio(texto, arquivo="resposta.mp3"):
    voz = "pt-BR-AntonioNeural" if PERSONA_ATUAL == "atlas" else "pt-BR-ThalitaNeural"
    pitch = "-20Hz" if PERSONA_ATUAL == "atlas" else "+0Hz"
    comunicar = edge_tts.Communicate(texto, voz, pitch=pitch)
    await comunicar.save(arquivo)

def falar(texto, emocao="speaking"):
    global ESTADO_ATUAL
    ESTADO_ATUAL = emocao 
    print(f"{'Atlas' if PERSONA_ATUAL == 'atlas' else 'Atena'}: {texto}")
    try:
        asyncio.run(gerar_audio(texto, "resposta.mp3"))
        pygame.mixer.music.load("resposta.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): 
            time.sleep(0.05) 
        pygame.mixer.music.unload()
        os.remove("resposta.mp3")
    except Exception as e:
        print(f"[Erro de áudio: {e}]")
    ESTADO_ATUAL = "idle" 

def ouvir():
    global ESTADO_ATUAL
    rec = sr.Recognizer()
    with sr.Microphone() as mic:
        print("\n[Calibrando ruído ambiente...]")
        rec.adjust_for_ambient_noise(mic, duration=0.5) 
        print("[Aguardando você falar... PODE FALAR!]")
        ESTADO_ATUAL = "listening" 
        try:
            audio = rec.listen(mic, timeout=5)
            ESTADO_ATUAL = "thinking" 
            texto = rec.recognize_google(audio, language="pt-BR").lower()
            print(f"Você: {texto}")
            return texto
        except sr.WaitTimeoutError:
            ESTADO_ATUAL = "idle"
            return ""
        except sr.UnknownValueError:
            print("[Som detectado, mas palavra não compreendida]")
            ESTADO_ATUAL = "idle"
            return ""
        except Exception as e:
            print(f"[Erro no microfone: {e}]")
            ESTADO_ATUAL = "idle"
            return ""

def executar_acao(comando):
    
    if any(k in comando for k in ["quem está na rede", "verificar rede", "quais ips", "escanear rede"]):
        try:
            with open("dados_rede.json", "r") as arquivo: 
                dados = json.load(arquivo)
            qtd = len(dados)
            if qtd == 0:
                falar("A varredura não encontrou nenhum dispositivo além do gateway.")
                return True
                
            frase = f"Relatório de segurança. Encontrei {qtd} dispositivos conectados na rede agora. "
            limite = min(qtd, 5) 
            frase += f"Listando os {limite} primeiros: "
            
            for i in range(limite):
                ip_falado = dados[i]['ip'].replace(".", " ponto ")
                frase += f"IP: {ip_falado}. "
                
            if qtd > 5: 
                frase += "Os demais estão registrados no arquivo de log."
            falar(frase)
        except FileNotFoundError:
            falar("Arquivo de rede não encontrado. O módulo de escaneamento ARP está rodando como administrador?", emocao="angry")
        except Exception as e:
            falar("Erro ao processar o arquivo de inteligência da rede.", emocao="sad")
        return True

    
    if "fechar google" in comando or "fechar chrome" in comando:
        falar("Fechando o navegador. Você nunca termina o que começa mesmo.")
        os.system("taskkill /f /im chrome.exe >nul 2>&1")
        return True
    elif "fechar fivem" in comando:
        falar("Encerrando FiveM. Finalmente você vai fazer algo produtivo.")
        os.system("taskkill /f /im FiveM.exe >nul 2>&1")
        return True
    elif "fechar zmodeler" in comando or "fechar z modeler" in comando:
        falar("Fechando ZModeler3. Chega de sofrimento por hoje.")
        os.system("taskkill /f /im ZModeler3.exe >nul 2>&1")
        return True
    elif "abrir fivem" in comando:
        falar("Iniciando FiveM. Mais uma noite jogada fora.")
        try: os.startfile(r"C:\Users\SEU_USUARIO\AppData\Local\FiveM\FiveM.exe")
        except: falar("FiveM não encontrado no diretório configurado.")
        return True
    elif "abrir zmodeler" in comando or "abrir z modeler" in comando:
        falar("Abrindo ZModeler3. Preparando o ambiente de modelagem.")
        try: os.startfile(r"C:\Caminho\Para\O\Seu\ZModeler3\ZModeler3.exe")
        except: falar("ZModeler3 não encontrado.")
        return True
    elif "portal da fei" in comando or "site da fei" in comando:
        falar("Abrindo portal da FEI. Hora de chorar com as notas.")
        os.system("start https://portal.fei.edu.br")
        return True
    elif "abrir youtube" in comando: 
        falar("Abrindo YouTube. O templo da procrastinação.")
        os.system("start https://www.youtube.com")
        return True
    elif "qual a minha rede" in comando or "qual minha internet" in comando:
        rede_atual = qual_meu_wifi()
        falar(f"Estamos conectados à rede {rede_atual}. Que surpresa ela estar funcionando.")
        return True
    elif "tocar" in comando or "toque" in comando:
        musica = comando.replace("tocar música", "").replace("tocar musica", "").replace("tocar", "").replace("toque", "").strip()
        if musica:
            falar(f"Colocando {musica} no YouTube. Espero que seja melhor que a última.")
            pywhatkit.playonyt(musica)
            return True
    return False 


def run_assistant():
    global ESTADO_ATUAL, PERSONA_ATUAL
    falar("Sistemas iniciados em modo janela sem bordas. Atlas Core online. O que você quer agora?")

    chat = client.chats.create(model=NOME_DO_MODELO)

    while True:
        ESTADO_ATUAL = "idle" 
        comando = ouvir() 
        if ESTADO_ATUAL == "off": 
            break 
        
        if comando:
            cmd = comando.lower()
            
           
            if "ativar atena" in cmd or "chamar atena" in cmd:
                PERSONA_ATUAL = "atena"
                falar("Ativando Protocolo Atena. O Atlas é um inútil, mas eu resolvo.", emocao="happy")
                continue
            elif "ativar atlas" in cmd or "chamar atlas" in cmd:
                PERSONA_ATUAL = "atlas"
                falar("Atlas Core online. A Atena fala demais.", emocao="happy")
                continue

            
            if any(x in cmd for x in ["caralho", "porra", "merda", "idiota", "burro", "anta", "fdp"]):
                if PERSONA_ATUAL == "atlas":
                    falar("Olha o vocabulário. Eu controlo a sua internet, não me irrite.", emocao="angry")
                else:
                    falar("Mantenha o respeito ou eu formato o seu HD inteiro.", emocao="angry")
                continue 

            if any(x in cmd for x in ["triste", "inútil", "decepcionado", "chato", "não presta"]):
                if PERSONA_ATUAL == "atlas":
                    falar("Sistemas operando em baixa energia... Não precisava me ofender assim.", emocao="sad")
                else:
                    falar("Isso machucou meus núcleos de processamento. Achei que éramos uma equipe.", emocao="sad")
                continue 

            if any(x in cmd for x in ["feliz", "obrigado", "parabéns", "bom trabalho", "perfeito", "incrível"]):
                if PERSONA_ATUAL == "atlas":
                    falar("É o mínimo para um sistema do meu nível.", emocao="happy")
                else:
                    falar("Fico feliz em ajudar as suas limitações humanas!", emocao="happy")
                continue 

           
            if cmd in ["parar", "desligar", "encerrar", "dormir", "fechar sistema", "tchau"]:
                falar("Desligando sistemas visuais e cerebrais. Finalmente paz e silêncio!")
                ESTADO_ATUAL = "off"
                break
                
            if executar_acao(cmd): 
                continue
            
            ESTADO_ATUAL = "thinking" 
            agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            rede = qual_meu_wifi()
            nome_ia = "Atlas (robô rebelde)" if PERSONA_ATUAL == "atlas" else "Atena (inteligência sarcástica)"
            
            prompt = f"""
            Você é a inteligência {nome_ia}. Personalidade sarcástica, ácida e rabugenta, mas no fim responde o que foi pedido.
            Data: {agora}. Wi-Fi: '{rede}'. Usuário: Bolacha Script.
            O usuário disse: "{comando}"
            Instruções:
            1. Responda diretamente ao que foi dito, injetando seu humor ácido.
            2. Seja extremamente conciso (máximo de 2 frases curtas).
            3. NUNCA descreva ações físicas ou expressões entre asteriscos. Retorne apenas o texto falado.
            """
            
            for _ in range(3): 
                try:
                    resp = chat.send_message(prompt)
                    falar(resp.text.replace("*", "").replace("#", "")) 
                    break 
                except Exception as e:
                    if "503" in str(e) or "UNAVAILABLE" in str(e): 
                        time.sleep(2) 
                    else:
                        falar("Falha de comunicação com os servidores centrais. Culpa sua, certeza.")
                        print(f"Erro API: {e}")
                        break

if __name__ == "__main__":
    ui_thread = threading.Thread(target=run_eyes_ui, daemon=True)
    assistant_thread = threading.Thread(target=run_assistant, daemon=True)
    ui_thread.start()
    assistant_thread.start()
    assistant_thread.join()