# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 12:55:55 2021

@author: JOEL
"""
import random, sys, time, math, pygame
from pygame.locals import *
#definimos contantes
FPS = 30 # fotogramas por segundo para actualizar la pantalla
WINWIDTH = 900 # ancho de la ventana del programa, en píxeles
WINHEIGHT = 820 # altura en píxeles 
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

COLOR_FONDO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)

CAMARAMOV = 90     # qué tan lejos del centro se mueve la bola antes de mover la cámara
MOV_JUGADOR = 10         # qué tan rápido se mueve el jugador
BOUNCERATE = 9       # qué tan rápido mueve el jugador (grande es más lento)
BOUNCEHEIGHT = 30    # qué tan alto rebota el jugador
STARTSIZE = 30       # qué tan grande comienza el jugador
WINSIZE = 200        # qué tan grande debe ser el jugador para ganar
INMORTAL = 4       # cuánto tiempo el jugador es invulnerable después de ser golpeado en segundos
GAMEOVERTIME = 4     # cuánto tiempo permanece el texto "game over" en la pantalla en segundos
VIDAS = 3        # con cuánta salud comienza el jugador
NUM_ESTRELLAS = 80        # número de objetos de estrellas en el área activa
NUM_JUGADORES = 30    # número de bolas en el área activa
JUGADOR_LENTO = 3 # velocidad de bolas más lenta
JUGADOR_VELOZ = 7 # velocidad de bolas más rápida
CAMBIO_DIRECCION = 2    #% de probabilidad de cambio de dirección por cuadro
IZQ = 'left'
DER = 'right'

def main():
    global FPSRELOJ, DISPLAYSURF, BASICFONT, L_BOLA_IMG, R_BOLA_IMG, ESTRELLAS,RAND_ESTRELLAS,RAND_BOLAS

    pygame.init() #INICIAMOS EL PYGAME
    FPSRELOJ = pygame.time.Clock() #CONTROLAMOS TIEMPO
    pygame.display.set_icon(pygame.image.load('gameicon.png'))#ICONO INCIAL
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))#TAMAÑO DE LA PANTALLA INCIAL
    pygame.display.set_caption('COME Y CRECE')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)#AYUDA A CONSULTAR VARIACIONES

    # carga los archivos de imagen
    L_BOLA_IMG = pygame.image.load('bola5.png')
    L_BOLA_IMG2 = pygame.image.load('bola1.png')
    L_BOLA_IMG3 = pygame.image.load('bola2.png')

    R_BOLA_IMG = pygame.transform.flip(L_BOLA_IMG, True, False)
    ESTRELLAS = []
    for i in range(1, 3):
        ESTRELLAS.append(pygame.image.load('estrellas%s.jpg' % i))

    while True:
        runGame()


def Dibuja_vidas(vida_actual):

    for i in range(vida_actual): # dibuja barras de salud rojas
        pygame.draw.rect(DISPLAYSURF, BLANCO,   (15, 5 + (10 * VIDAS) - i * 10, 20, 10))
        #pygame.display.set_icon(pygame.image.load('corazon.jpg'))
    for i in range(VIDAS): # dibuja los contornos blancos
        pygame.draw.rect(DISPLAYSURF,BLANCO, (15, 5 + (10 * VIDAS) - i * 10, 20, 10), 1)


def terminar():
    pygame.quit()
    sys.exit()

def Vel_aletoria():
    speed = random.randint(JUGADOR_LENTO, JUGADOR_VELOZ)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def Pos_alea_camara(camerax, cameray, objWidth, objHeight):
    # crea un Recto de la vista de la cámara
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # crea un objeto Rect con las coordenadas aleatorias y usa colliderect ()
        # para asegurarse de que el borde derecho no esté en la vista de la cámara.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y

def Personaje_iz_der(camerax, cameray):
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width']  = (generalSize + random.randint(0, 10)) * multiplier
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = Pos_alea_camara(camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = Vel_aletoria()
    sq['movey'] = Vel_aletoria()
    if sq['movex'] < 0: # personaje está mirando hacia la izquierda
        sq['surface'] = pygame.transform.scale(L_BOLA_IMG, (sq['width'], sq['height']))
    else: # personaje está mirando a la derecha
        sq['surface'] = pygame.transform.scale(R_BOLA_IMG, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq

def Nuevas_estrellas(camerax, cameray):
    gr = {}
    gr['grassImage'] = random.randint(0, len(ESTRELLAS) - 1)
    gr['width']  = ESTRELLAS[0].get_width()
    gr['height'] = ESTRELLAS[0].get_height()
    gr['x'], gr['y'] = Pos_alea_camara(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr

def Sale_fuera_pantalla(camerax, cameray, obj):
    #  Devuelve False si camerax y cameray son más de
    #  una media ventana más allá del borde de la ventana.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)

def runGame():
    # configurar variables para el inicio de un nuevo juego
    invulnerableMode = False  # si el jugador es invulnerable
    invulnerableStartTime = 0 # vez que el jugador se volvió invulnerable
    gameOverMode = False      # si el jugador ha perdido
    gameOverStartTime = 0     # tiempo que el jugador perdió
    winMode = False           # si el jugador ha ganado

    # crea las superficies para contener el texto del juego
    gameOverSurf = BASICFONT.render('Intentalo de nuevo', True, BLANCO)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('ganaste!!!!', True, BLANCO)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(pulsa espace para empezar de nuevo.)', True, BLANCO)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # camerax y cameray son el punto medio de la vista de la cámara.
    camerax = 0
    cameray = 0

    grassObjs = []    # almacena todos los objetos de hierba del juego
    squirrelObjs = [] # almacena todos los objetos de ardilla que no son jugadores
    # almacena el objeto del jugador:
    playerObj = {'surface': pygame.transform.scale(L_BOLA_IMG, (STARTSIZE, STARTSIZE)),
                 'facing':  IZQ,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0,
                 'health': VIDAS}

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False

    # comienza con algunas imágenes de césped al azar en la pantalla
    for i in range(10):
        grassObjs.append(Nuevas_estrellas(camerax, cameray))
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True: # bucle principal del juego
        # Comprueba si debemos desactivar la invulnerabilidad
        if invulnerableMode and time.time() - invulnerableStartTime > INMORTAL:
            invulnerableMode = False

        # mueve todas las ardillas
        for sObj in squirrelObjs:
            # mueve la ardilla y ajusta su rebote
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0 # restablecer la cantidad de rebote

            # posibilidad aleatoria de que cambien de dirección
            if random.randint(0, 99) < CAMBIO_DIRECCION:
                sObj['movex'] = Vel_aletoria()
                sObj['movey'] = Vel_aletoria()
                if sObj['movex'] > 0: # mira hacia la derecha
                    sObj['surface'] = pygame.transform.scale(R_BOLA_IMG, (sObj['width'], sObj['height']))
                else: # caras a la izquierda
                    sObj['surface'] = pygame.transform.scale(L_BOLA_IMG, (sObj['width'], sObj['height']))


        # revise todos los objetos y vea si es necesario eliminar alguno.
        for i in range(len(grassObjs) - 1, -1, -1):
            if Sale_fuera_pantalla(camerax, cameray, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(squirrelObjs) - 1, -1, -1):
            if Sale_fuera_pantalla(camerax, cameray, squirrelObjs[i]):
                del squirrelObjs[i]

        # agregue más pasto y ardillas si no tenemos suficiente.
        while len(grassObjs) < NUM_ESTRELLAS:
            grassObjs.append(Nuevas_estrellas(camerax, cameray))
        while len(squirrelObjs) < NUM_JUGADORES:
            squirrelObjs.append(Personaje_iz_der(camerax, cameray))

        # ajuste camerax y cameray si está más allá de la "holgura de la cámara"
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMARAMOV:
            camerax = playerCenterx + CAMARAMOV - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMARAMOV:
            camerax = playerCenterx - CAMARAMOV - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMARAMOV:
            cameray = playerCentery + CAMARAMOV - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMARAMOV:
            cameray = playerCentery - CAMARAMOV - HALF_WINHEIGHT

        #dibuja el fondo PANTALLA
        DISPLAYSURF.fill(COLOR_FONDO)

        # dibuja todos los objetos de hierba en la pantalla
        for gObj in grassObjs:
            gRect = pygame.Rect( (gObj['x'] - camerax,
                                  gObj['y'] - cameray,
                                  gObj['width'],
                                  gObj['height']) )
            DISPLAYSURF.blit(ESTRELLAS[gObj['grassImage']], gRect)


        #  dibuja las otras bolas
        for sObj in squirrelObjs:
            sObj['rect'] = pygame.Rect( (sObj['x'] - camerax,
                                         sObj['y'] - cameray ,
                                         sObj['width'],
                                         sObj['height']) )
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])


        # dibuja la bola del jugador
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray,
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])


        # dibuja el medidor de salud
        Dibuja_vidas(playerObj['health'])

        for event in pygame.event.get(): # bucle de manejo de eventos
            if event.type == QUIT:
                terminar()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != IZQ: #  cambia la imagen del
                        playerObj['surface'] = pygame.transform.scale(L_BOLA_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = IZQ
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != DER: # cambia la imagen del
                        playerObj['surface'] = pygame.transform.scale(R_BOLA_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = DER
                elif winMode and event.key == K_r:
                    return

            elif event.type == KEYUP:
                # deja de mover la ardilla del jugador
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminar()

        if not gameOverMode:
            # realmente mueve al jugador
            if moveLeft:
                playerObj['x'] -= MOV_JUGADOR
            if moveRight:
                playerObj['x'] += MOV_JUGADOR
            if moveUp:
                playerObj['y'] -= MOV_JUGADOR
            if moveDown:
                playerObj['y'] += MOV_JUGADOR

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 0

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0 # restablecer la cantidad de rebote

            # comprobar si el jugador ha chocado con alguna ardilla
            for i in range(len(squirrelObjs)-1, -1, -1):
                sqObj = squirrelObjs[i]
                if 'rect' in sqObj and playerObj['rect'].colliderect(sqObj['rect']):
                    # se ha producido una colisión entre jugador y ardilla

                    if sqObj['width'] * sqObj['height'] <= playerObj['size']**2:
                        #  jugador es más grande y se come a la ardilla
                        playerObj['size'] += int( (sqObj['width'] * sqObj['height'])**0.2 ) + 1
                        del squirrelObjs[i]

                        if playerObj['facing'] == IZQ:
                            playerObj['surface'] = pygame.transform.scale(L_BOLA_IMG, (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == DER:
                            playerObj['surface'] = pygame.transform.scale(R_BOLA_IMG, (playerObj['size'], playerObj['size']))

                        if playerObj['size'] > WINSIZE:
                            winMode = True # activa el "modo win"

                    elif not invulnerableMode:
                        # jugador es más pequeño y recibe daño
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode = True # activa el "modo de fin de juego"
                            gameOverStartTime = time.time()
        else:
            # juego ha terminado, muestra el texto "juego terminado"
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return # finaliza el juego actual

        # comprobar si el jugador ha ganado.
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        FPSRELOJ.tick(FPS)



if __name__ == '__main__':
    main()
