from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, sys

class Tracker:
    """ Master class """
    def __init__(self):
        self.window = self.initWindow()
        self.run()

    def initWindow(self):
        # pygame.display.set_caption(self.windowTitle)
        pygame.font.init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode( (1280,900) )
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

    def run(self):
        MainScreen(tracker=self)

class Screen:
    """ Screen Template Class """
    def __init__(self, tracker):
        self.clock = tracker.clock
        self.screen = tracker.screen
        self.colors = Colorscheme()
        self.run()
    
    """ Main screen loop """
    def run(self):
        while True:
            self.clock.tick(60)/1000
            self.screen.fill( self.colors.bg )

            key = self.keyHandler()
            if key!=None:
                print(key)

            pygame.display.flip()
    
    def getEvents(self):
        events = []
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    sys.exit()
            elif event.type==pygame.QUIT:
                sys.exit()
            events.append(event)
        return events

class Colorscheme:
    """ Colors """
    def __init__(self):

        """ colors """
        self.black = (0,0,0)

        """ interface elements """
        self.bg = self.black

class MainScreen(Screen):
    """ Main screen loop """
    def run(self):
        while True:
            self.clock.tick(60)/1000
            self.screen.fill( self.colors.bg )

            self.keyHandler(self.getEvents())
            
            pygame.display.flip()

    def keyHandler(self, events):
        pass
