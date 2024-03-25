import pygame
from build_colour_dct import build_colour_dct
from collections import deque,defaultdict
from queue import PriorityQueue 
 
CD = build_colour_dct()
pygame.init()
# test_surface = pygame.Surface((32,32))
# test_surface.fill(CD['RED'])
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 816

GRID_WIDTH = 800
GRID_HEIGHT = 784
GAP = 16

TOOLBAR_WIDTH = 800
TOOLBAR_HEIGHT = 32

BUTTON_WIDTH = 800//4
BUTTON_HEIGHT = 16

class Button:

    def __init__(self,width,height,value):
        pygame.init()
        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width,self.height))
        self.active = False
        self.colour = 'BLUE'
        self.image.fill(CD['BLUE'])
        self.value = value
    
    
    def add_text(self,text,text_colour,background_colour):
     
        font = pygame.font.Font('freesansbold.ttf', 16)
        text = font.render(text,True,CD[text_colour],CD[background_colour])
        textRect = text.get_rect()
        textRect.center = (self.width//2,self.height//2)
        self.image.blit(text,textRect)

class Toolbar:

    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width,self.height))
        self.rect = self.image.get_rect()
        self.image.fill(CD['BLACK'])
    # def button_pos(self):
        self.text = ['BFS','A*']
        self.no_of_buttons = len(self.text)
        W = self.width//self.no_of_buttons
        H = self.height
        self.buttons = []
        for i in range(self.no_of_buttons):
            x,y = i*W,0
            t = self.text[i]
            B = Button(W,H,t)
            B.add_text(t,'PURPLE','BLUE')
            self.buttons.append(B)
            self.image.blit(B.image,(x,y))
        for i in range(self.no_of_buttons+1):
            pygame.draw.line(self.image,CD['GREY'],(i*W,0),(i*W,H))

    def draw_buttons(self):
        W = self.width//self.no_of_buttons
        H = self.height
        for i in range(self.no_of_buttons):
            B = self.buttons[i]
            B.image.fill(CD[B.colour])
            B.add_text(B.value,'PURPLE',B.colour)
            self.image.blit(B.image,(i*W,0))
        for i in range(self.no_of_buttons+1):
            pygame.draw.line(self.image,CD['GREY'],(i*W,0),(i*W,H))
        
    def update_buttons(self,idx):
        B = self.buttons[idx]
        for i in range(len(self.buttons)):
            if i != idx:
                B1 = self.buttons[i]
                B1.colour = 'BLUE'
                B1.active = False
        B.colour = 'RED'
        B.active = True
        self.draw_buttons()

    def return_width(self):
        return self.width//self.no_of_buttons

    def return_button_value(self):
        for button in self.buttons:
            if button.active:
                return button.value

class Node:

    def __init__(self,gap):
        self.gap = gap
        self.colour = CD['WHITE']
        self.x = None
        self.y = None
        self.neighbors = []
        self.steps_from_start = float('inf')


    def reset(self):
        self.colour = CD['WHITE']

    def make_start(self):
        self.colour = CD['ORANGE']

    def make_end(self):
        self.colour = CD['TURQUOISE']
    
    def make_barrier(self):
        self.colour = CD['BLACK']

    def make_processing(self):
        self.colour = CD['RED']
    
    def make_processed(self):
        self.colour = CD['GREEN']
    
    def make_path(self):
        self.colour = CD['PURPLE']
    
    def is_start(self):
        return self.colour == CD['ORANGE']
    
    def is_end(self):
        return self.colour == CD['TURQUOISE']
    
    def available(self):
        return self.colour == CD['WHITE']

    def checked(self):
        return self.colour == CD['GREEN']
    
    def is_processing(self):
        return self.colour == CD['RED']

    def is_processed(self):
        return self.colour == CD['GREEN']
    
    def is_barrier(self):
        return self.colour == CD['BLACK']

class PriorityQueueElement:
    def __init__(self, priority, value):
        self.priority = priority
        self.value = value
    
    def __lt__(self, other):
        if self.priority == other.priority:
            # Here you can decide on a secondary comparison.
            # For simplicity, we'll just consider all elements with the same priority as equal,
            # and hence not less than each other, so we return False.
            # Alternatively, you could use id(self) < id(other) to order by object id as a last resort.
            return False
        return self.priority < other.priority

class Grid:
    def __init__(self,width,height,gap):
        self.gap = gap
        self.width = width
        self.height = height
        self.image = pygame.Surface((width,height))
        self.image.fill(CD['WHITE'])
        no_of_nodes = (self.width//gap)*(self.height//gap)
        W = self.width//gap
        H = self.height //gap
        self.grid = []
        for i in range(H):
            line = []
            for j in range(W):
                N = Node(GAP)
                N.x = j*GAP
                N.y = i*GAP
                line.append(N)
            self.grid.append(line)
        self.start = False
        self.end = False

    def start_selected(self):
        return self.start
    
    def end_selected(self):
        return self.end

    def draw_grid(self):
        W = self.width//self.gap
        H = self.height//self.gap

        for i in range(W+1):
            pygame.draw.line(self.image,CD['GREY'],(i*self.gap,0),(i*self.gap,self.height))
        for i in range(H+1):
            pygame.draw.line(self.image,CD['GREY'],(0,i*self.gap),(self.width,i*self.gap))

        pygame.display.update()


    def update_node(self,y,x,click):
        node = self.grid[y][x]
        if click == 'left':
            if not self.start_selected():
                node.make_start()
                self.start = True
            
            if not node.is_start() and not self.end_selected():
                node.make_end()
                self.end = True

            else:
                if not node.is_start() and not node.is_end():
                    node.make_barrier()
        elif click == 'right':
            if node.is_start():
                self.start = False
            elif node.is_end():
                self.end = False
            node.reset()

        pygame.draw.rect(self.image,node.colour,(node.x,node.y,self.gap,self.gap))
        self.draw_grid()

def find_start(win):

    start = False
    for line in win.grid:
        for node in line:
            if node.is_start():
                start = node

    return start

def find_end(win):
    end = False
    for line in win.grid:
        for node in line:
            if node.is_end():
                end = node

    return end

    
def bfs(win,start_node,clock,screen):
    
    Q = deque()
    Q.append((start_node,[]))
    DIRS = [(1,0),(-1,0),(0,1),(0,-1)]
    c = 0

    while Q: # and c < 10:

        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elem,path = Q.popleft()
        new_lst = [_ for _ in path]
        new_lst.append(elem)
        y,x = elem.y//16,elem.x//16
        if elem.is_end():
            return path[::-1]
        if not elem.is_start():
            elem.make_processed()
            win.update_node(elem.y//16,elem.x//16,'none')
            screen.blit(win.image,(0,TOOLBAR_HEIGHT))
        lst = []
        for dy,dx in DIRS:
            yy,xx = y+dy,x+dx
            if 0 <= yy < win.height//win.gap and 0 <= xx < win.width//win.gap:
                new_node = win.grid[yy][xx]
            if not new_node.is_start() and not new_node.is_barrier() and not new_node.is_processing() and not new_node.is_processed():
                lst.append(new_node)

        for node in lst:
            clock.tick(100)
            if not node.is_end():
                node.make_processing()
                win.update_node(node.y//16,node.x//16,'none')
            Q.append((node,new_lst))
            screen.blit(win.image,(0,TOOLBAR_HEIGHT))


def h(p1, p2):
	y1,x1 = p1
	y2,x2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def a_star(win,start_node,end_node,clock,screen):
    
    end_y,end_x = end_node.y//16,end_node.x//16
    start_y,start_x = start_node.y//16,start_node.x//16
    start_f = h((start_y,start_x),(end_y,end_x))

    Q = PriorityQueue()
    Q.put((start_f,0,start_y,start_x))
    DIRS = [(1,0),(-1,0),(0,1),(0,-1)]
    came_from = defaultdict(list)
    came_from[start_node].append(start_node)
    # print(came_from)
    # return
    


    while not Q.empty():
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        f,steps,y,x = Q.get()
        curr = win.grid[y][x]
        
        if curr.is_end():
            return came_from[curr][::-1]
        
        if not curr.is_start():
            curr.make_processed()
            win.update_node(y,x,'none')
            screen.blit(win.image,(0,TOOLBAR_HEIGHT))

        lst = []
        for dy,dx in DIRS:
            yy,xx = y+dy,x+dx
        
            if 0<=yy<win.height//16 and 0<=xx<win.width//16:
                new_node = win.grid[yy][xx]
                new_lst = [i for i in came_from[curr]]
                new_lst.append(new_node)
                # print(new_lst)
                came_from[new_node] = new_lst
                new_steps = steps + 1
                h_score = h((yy,xx),(end_y,end_x))
                f_score = h_score + new_steps
        
                if not new_node.is_start() and not new_node.is_barrier() and not new_node.is_processing() and not new_node.is_processed():
                    lst.append([f_score,new_steps,yy,xx])
        

        for f_score,steps,new_y,new_x in lst:
            clock.tick(100)
            node = win.grid[new_y][new_x]
            if not node.is_end():
                node.make_processing()
                win.update_node(node.y//16,node.x//16,'none')
            Q.put((f_score,steps,new_y,new_x))
            screen.blit(win.image,(0,TOOLBAR_HEIGHT))
    
    

def path_vis(lst,win,screen,clock):

    for node in lst:
        clock.tick(50)
        if not node.is_start() and not node.is_end():
            node.make_path()
        win.update_node(node.y//16,node.x//16,'none')
        screen.blit(win.image,(0,TOOLBAR_HEIGHT))

    return True




def main():
     

    pygame.init()   
    T = Toolbar(TOOLBAR_WIDTH,TOOLBAR_HEIGHT)
    G = Grid(GRID_WIDTH,GRID_HEIGHT,GAP)
    # pygame.display.set_caption("minimal program")
    SCREEN = pygame.display.set_mode((800,800))
    SCREEN.blit(G.image,(0,TOOLBAR_HEIGHT))
    CLOCK = pygame.time.Clock()
    reset = False
  
    global running
    running = True
    G.draw_grid()
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            tbar = SCREEN.blit(T.image,(0,0))
            pos = pygame.mouse.get_pos()
            grid_obj = SCREEN.blit(G.image,(0,TOOLBAR_HEIGHT))
            

            if tbar.collidepoint(pos):
                    if pygame.mouse.get_pressed()[0]:
                        x_coord = pos[0]//T.return_width()
                        y_coord = pos[1]//TOOLBAR_HEIGHT
                        T.update_buttons(x_coord)
            elif grid_obj.collidepoint(pos):
                x_coord = pos[0]//GAP
                y_coord = (pos[1]-32)//GAP
                
                if pygame.mouse.get_pressed()[0]:
                    if reset:
                        G = Grid(GRID_WIDTH,GRID_HEIGHT,GAP)
                        grid_obj = SCREEN.blit(G.image,(0,TOOLBAR_HEIGHT))
                        reset = False
                    G.update_node(y_coord,x_coord,'left')
                if pygame.mouse.get_pressed()[2]:
                    G.update_node(y_coord,x_coord,'right')

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:

                    start = find_start(G)
                    end = find_end(G)
                    if not start or not end:
                        continue
                    else:
                        x = False
                        for button in T.buttons:
                            if button.active:
                                value = button.value
                                if value == 'A*':
                                    x = a_star(G,start,end,CLOCK,SCREEN)
                                else:
                                    x = bfs(G,start,CLOCK,SCREEN)
                        reset = True
                        

                   
        pygame.display.flip()
    pygame.quit()
     
 
main()

