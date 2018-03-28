import sys
import time
import pygame
import requests
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw, ImageWin
import win32print, win32api, win32con, win32ui
from ConfigParser import ConfigParser
import logging

config = ConfigParser()
config.read("ingreso.conf")

#Resolucion de pantalla...
SCREEN_WIDTH = int(config.get("GENERAL", "SCREEN_WIDTH"))
SCREEN_HEIGHT = int(config.get("GENERAL", "SCREEN_HEIGHT"))
#Si escribe logs
LOG_FILE = config.get("GENERAL", "LOG_FILE")
#Entorno: DES=DESARROLLO, PRD=PRODUCCION
#Si ENTORNO = DES no imprime ticket y se visualiza el puntero del mouse
ENTORNO = config.get("GENERAL", "ENTORNO")
#Configuracion de ticket
#**************************************************************
VISIBLE_T = config.get("TICKET", "VISIBLE")
if VISIBLE_T == "SI":
    IMAGEN_T = config.get("TICKET", "IMAGEN")
    COORDENADA_X_T = int(config.get("TICKET", "COORDENADA_X"))
    COORDENADA_Y_T = int(config.get("TICKET", "COORDENADA_Y"))
#Configuracion de botones
#**************************************************************
VISIBLE_1 = config.get("BOTON_1", "VISIBLE")
if VISIBLE_1 == "SI":
    IMAGEN_1 = config.get("BOTON_1", "IMAGEN")
    COORDENADA_X_1 = int(config.get("BOTON_1", "COORDENADA_X"))
    COORDENADA_Y_1 = int(config.get("BOTON_1", "COORDENADA_Y"))
    TEXTO_1 = config.get("BOTON_1", "TEXTO")
    URL_TRAMITE_1 = config.get("BOTON_1", "URL_TRAMITE")
#**************************************************************
VISIBLE_2 = config.get("BOTON_2", "VISIBLE")
if VISIBLE_2 == "SI":
    IMAGEN_2 = config.get("BOTON_2", "IMAGEN")
    COORDENADA_X_2 = int(config.get("BOTON_2", "COORDENADA_X"))
    COORDENADA_Y_2 = int(config.get("BOTON_2", "COORDENADA_Y"))
    TEXTO_2 = config.get("BOTON_2", "TEXTO")
    URL_TRAMITE_2 = config.get("BOTON_2", "URL_TRAMITE")
#**************************************************************

class Cursor(pygame.Rect):
    def __init__(self):
        pygame.Rect.__init__(self,0,0,1,1)
    def update(self):
        self.left,self.top=pygame.mouse.get_pos()

class Boton(pygame.sprite.Sprite):
    def __init__(self,imagen1,imagen2,x=0,y=0):
        self.imagen_normal=imagen1
        self.imagen_seleccion=imagen2
        self.imagen_actual=self.imagen_normal
        self.rect=self.imagen_actual.get_rect()
        self.rect.left,self.rect.top=(x,y)
    def update(self,screen,cursor):
        if cursor.colliderect(self.rect):
            self.imagen_actual=self.imagen_seleccion
        else: self.imagen_actual=self.imagen_normal
        screen.blit(self.imagen_actual,self.rect)

def text(texto, color, posicion, size, screen):
    fuente = pygame.font.SysFont("Arial Black", size)
    render = fuente.render(str(texto), 1, color)
    screen.blit(render, posicion)

def printTicket(letraTicket, numeroTurno, tiempoEspera, fechaTurno, logger):
    log("Inicio de generacion de Ticket", logger)
    fuente1 = ImageFont.truetype("arial.ttf", 72)
    fuente2 = ImageFont.truetype("arial.ttf", 36)
    fuente3 = ImageFont.truetype("arial.ttf", 18)
    imagenTicket = Image.new("RGBA",(400,200),(255,255,255))
    draw = ImageDraw.Draw(imagenTicket)
    draw.text((95,10), letraTicket + " " + numeroTurno, font=fuente1, fill=(55,55,55))
    draw.text((10,100), fechaTurno, font=fuente2, fill=(55,55,55))
    draw.text((10,160), tiempoEspera, font=fuente3, fill=(55,55,55))
    del draw
    imagenTicket.save('ticket.png', "PNG")
    log("Fin de generacion de Ticket", logger)
    if ENTORNO == "PRD":
        execfile("print.py")

def mousePos(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def log(text, logger):
    if LOG_FILE == "SI":
        logger.info(text)

#Funcion main
def main():
    #Inicializa logging
    logger = logging.getLogger('ingreso')
	
    if LOG_FILE == "SI":
        nombreLog = 'Logs\%s' % time.strftime("%Y-%m-%d")
        hdlr = logging.FileHandler('%s.log' % nombreLog)
	
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)

    log("", logger)
    log("Inicio de la aplicacion", logger)

    pygame.init() #Inicializa el modulo

    #Fija las dimensiones de la pantalla
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Ingreso") # Titulo de la Ventana

    #Carga de la imagen de fondo
    fondo = pygame.image.load("background.jpg").convert_alpha()
    screen.blit(fondo, (0,0))

    #Crea un reloj para controlar los fps
    reloj = pygame.time.Clock()

    boton1 = None
    boton2 = None
    jsonBoton = []
    imprimir = False
    procesando = False

    if VISIBLE_T == "SI":
        imagenTA = pygame.image.load(IMAGEN_T+".png")
        imagenTB = pygame.image.load(IMAGEN_T+".png")
        ticket = Boton(imagenTA, imagenTB, COORDENADA_X_T, COORDENADA_Y_T)
    if VISIBLE_1 == "SI":
        imagen1A = pygame.image.load(IMAGEN_1+"A.png")
        imagen1B = pygame.image.load(IMAGEN_1+"B.png")
        boton1 = Boton(imagen1A, imagen1A, COORDENADA_X_1, COORDENADA_Y_1)
    if VISIBLE_2 == "SI":
        imagen2A = pygame.image.load(IMAGEN_2+"A.png")
        imagen2B = pygame.image.load(IMAGEN_2+"B.png")
        boton2 = Boton(imagen2A, imagen2A, COORDENADA_X_2, COORDENADA_Y_2)

    cursor = Cursor()
    if ENTORNO == "PRD":
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

    #LOOP PRINCIPAL
    while True:

        try:
            #Recorre todos los eventos producidos
            for event in pygame.event.get():
                cursor.update()
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if VISIBLE_1 == "SI":
                        if cursor.colliderect(boton1.rect) and procesando == False:
                            procesando = True
                            #Solicita ticket
                            log("", logger)
                            log("Solicitud: " + URL_TRAMITE_1, logger)
                            r = requests.get(URL_TRAMITE_1)
                            log("Respuesta: " + r.text, logger)
                            if r.status_code == 200:
                                jsonBoton = r.json()
                                imprimir = True
                                screen.blit(imagen1B, (COORDENADA_X_1, COORDENADA_Y_1))
                                pygame.display.flip()
                                pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
                    if VISIBLE_2 == "SI":
                        if cursor.colliderect(boton2.rect) and procesando == False:
                            procesando = True
                            #Solicita ticket
                            log("", logger)
                            log("Solicitud: " + URL_TRAMITE_2, logger)
                            r = requests.get(URL_TRAMITE_2)
                            log("Respuesta: " + r.text, logger)
                            if r.status_code == 200:
                                jsonBoton = r.json()
                                imprimir = True
                                screen.blit(imagen2B, (COORDENADA_X_2, COORDENADA_Y_2))
                                pygame.display.flip()
                                pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)

            reloj.tick(20) #Operacion para que todo corra a 20fps

            if VISIBLE_T == "SI":
                ticket.update(screen, cursor)
            if VISIBLE_1 == "SI":
                boton1.update(screen, cursor)
                text(TEXTO_1, (255,255,255), (COORDENADA_X_1+20,COORDENADA_Y_1+16), 48, screen)
            if VISIBLE_2 == "SI":
                boton2.update(screen, cursor)
                text(TEXTO_2, (255,255,255), (COORDENADA_X_2+20,COORDENADA_Y_2+16), 48, screen)

            if jsonBoton != []:
                if (str(jsonBoton['numeroTurno']) != "0"):
                    if VISIBLE_T == "SI":
                        text(jsonBoton['letraTicket'], (40,40,40), (220,20), 48, screen)
                        if len(jsonBoton['letraTicket']) == 1:
                            text(jsonBoton['numeroTurno'], (40,40,40), (260,20), 48, screen)
                        else:
                            text(jsonBoton['numeroTurno'], (40,40,40), (300,20), 48, screen)
                        text("Espera: " + jsonBoton['tiempoEspera'], (40,40,40), (220,85), 32, screen)
                        text(jsonBoton['fechaTurno'], (40,40,40), (220,140), 24, screen)
                    if imprimir == True:
                        printTicket(jsonBoton['letraTicket'], str(jsonBoton['numeroTurno']), "Espera: " + jsonBoton['tiempoEspera'], jsonBoton['fechaTurno'], logger)
                        time.sleep(3.2)
                        pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)

            if imprimir == True:
                imprimir = False
                pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)

            pygame.display.update() #Actualiza el display
            time.sleep(0.1)
            procesando = False

        except Exception, e:
            procesando = False
            logger.info("Salida por except: " + str(e))
            pass

    pygame.quit()

main()