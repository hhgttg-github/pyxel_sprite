import pyxel

#=======================================
# UTILITY

def sign(x):
    if x > 0:
        return(1)
    elif x < 0:
        return(-1)
    else:
        return(0)
    
#---------------------------------------
#
# nxn が各何行あるか。イメージバンクの256x256内の割当領域

DOT2      = 2       # 2dot = 128sp x 2行(256sp)
DOT2_Y    = 0
DOT2_ROW  = 2

DOT4      = 4       # 4dot = 64sp x 3行(192sp)
DOT4_Y    = 4
DOT4_ROW  = 3

DOT8      = 8        # 8dot = 32sp x 10行 (320sp)
DOT8_Y    = 16
DOT8_ROW  = 8

DOT16     = 16       # 16dot = 16sp x 4行(64sp)
DOT16_Y   = 96
DOT16_ROW = 4

DOT32     = 32       # 32dot = 8sp x 3行（24sp)
DOT32_Y   = 160
DOT32_ROW = 3

THRESHOULD = 1024
THRESHOULD_BIT = 10

SCREEN_LEFT   = 0
SCREEN_TOP    = 0
SCREEN_RIGHT  = 255
SCREEN_BOTTOM = 255
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256

OVER_LEFT   = -8
OVER_TOP    = -8
OVER_RIGHT  = 263
OVER_BOTTOM = 263
OVER_WIDTH = 272
OVER_HEIGHT = 272

#---------------------------------------
# 衝突判定（線分同士と正方形同士）

def check_segment(a1, b1, a2, b2):
    if a1 > a2:
        a1, a2 = a2, a1
        b1, b2 = b2, b1
    s1 = (a1-a2)*(b1-b2)
    s2 = (a1-b2)*(b1-a2)
    if (s2 == 0) or ((s1 > 0) and (s2 > 0)):
        return(False)
    else:
        return(True)

def check_rect(x1, y1, s1, x2, y2, s2):
    print("seg 1 " , check_segment(x1, x1+s1, x2, x2+s2))
    print("seg 2 " , check_segment(y1, y1+s1, y2, y2+s2))
    if check_segment(x1, x1+s1, x2, x2+s2) and check_segment(y1, y1+s1, y2, y2+s2):
        return(True)
    else:
        return(False)

def sprite_collision(sp1, sp2):
    x1 = sp1.x + sp1.hit
    y1 = sp1.y + sp1.hit
    s1 = sp1.h - sp1.hit * 2
    x2 = sp2.x + sp2.hit
    y2 = sp2.y + sp2.hit
    s2 = sp2.h - sp2.hit * 2
    return(check_rect(x1,y1,s1,x2,y2,s2))

#---------------------------------------

class SpGroup():
    """イメージ番号・スプライトサイズ・イメージ上の左上のy座標・それに続く行数
        my_resourceで8x8のキャラなら一行あたり横３２キャラクター並ぶ。"""
    def __init__(self, img, h, w, top , row):
        self.sheet_width  = 256
        self.sheet_height = 256
        self.img = img
        self.h   = h
        self.w   = w
        self.top = top
        self.row = row
        self.id_list = []
        for y in range(row):
            for x in range (self.sheet_width // self.w):
                 self.id_list.append((x*self.w, top + y*self.h))
    
    def return_uv(self, id):
        return(self.id_list[id][0], self.id_list[id][1])

sp2Group  = SpGroup(0, DOT2, DOT2, DOT2_Y, DOT2_ROW)
sp4Group  = SpGroup(0, DOT4, DOT4, DOT4_Y, DOT4_ROW)
sp8Group  = SpGroup(0, DOT8, DOT8, DOT8_Y, DOT8_ROW)
sp16Group = SpGroup(0, DOT16,DOT16, DOT16_Y, DOT16_ROW)
sp32Group = SpGroup(0, DOT32,DOT32, DOT32_Y, DOT32_ROW)

#---------------------------------------

class SpList():
    def __init__(self):
        self.list=[]

    def add(self, sp):
        self.list.append(sp)

    def all_dxdy(self, dx, dy):
        for i in range[self.list]:
            i.dx = dx
            i.dy = dy
    def all_dx(self, dx):
        for i in range[self.list]:
            i.dx = dx
    def all_dy(self, dy):
        for i in range[self.list]:
            i.dy = dy
    def update(self):
        for i in self.list:
            i.update()
    def draw(self):
        for i in self.list:
            i.draw()
            
#---------------------------------------
# SIMPLE SPRITE

class Sprite():
    def __init__(self, x, y, id, hit, sp_group):
        self.x = x
        self.y = y
        self.sp_group = sp_group
        self.img = sp_group.img
        self.id  = id
        self.h = sp_group.h
        self.w = sp_group.w
        self.u   = sp_group.id_list[self.id][0]
        self.v   = sp_group.id_list[self.id][1]
        self.show = True
        self.dx = 0
        self.prev_dx = 0
        self.dy = 0
        self.prev_dy = 0
        self.tx = 0
        self.ty = 0
        self.hit = hit
        self.hit_h = self.h - hit * 2
        self.hit_w = self.w - hit * 2
            
    def update(self):
        if (((self.dx > 0) and (self.prev_dx < 0)) or 
            ((self.dx < 0) and (self.prev_dx > 0))):
            self.tx = 0
            self.prev_dx = self.dx
        if (((self.dy > 0) and (self.prev_dy < 0)) or 
            ((self.dy < 0) and (self.prev_dy > 0))):
            self.ty = 0
            self.prev_dy = self.dy
        self.tx += self.dx
        self.ty += self.dy
        if abs(self.tx) >= THRESHOULD:
#            self.x += round(self.tx/THRESHOULD)
            self.x += self.tx >> THRESHOULD_BIT
            self.tx = 0
        if abs(self.ty) >= THRESHOULD:
#            self.y += round(self.ty/THRESHOULD)
            self.y += self.ty >> THRESHOULD_BIT
            self.ty = 0
    
    def draw(self):
        if self.show:
            pyxel.blt(self.x, self.y, self.img,
                    self.u, self.v, self.h, self.w, 0)
            
    def speed(self,dx,dy):
        self.dx = dx
        self.dy = dy
    
    def check_collision(self, sp):
        sprite_collision(self, sp)

#=======================================
#
# SWITCHING SPRITE

class SwitchingSp(Sprite):
    def __init__(self, x, y, id, hit, interval, sp_group):
        super().__init__(x, y, id, hit, sp_group)
        self.start = pyxel.frame_count
        self.interval = interval
        self.next = self.start + interval
        self.current = 0
        self.switch_table = (1,0)

    def update(self):
        super().update()
        if self.next <= pyxel.frame_count:
            self.current = self.switch_table[self.current]
            self.u, self.v = self.sp_group.return_uv(self.id + self.current)
            self.next = pyxel.frame_count + self.interval

#=======================================
#
# ANIMATED SPRITE (正方形のみ)

class AniSprite(Sprite):

    def __init__(self,x,y,id,hit,interval,key,sp_group): #idは最初の画像番号
        super().__init__(x,y,id,hit,sp_group)
        
        self.start = pyxel.frame_count
        self.interval = interval #60fps なので60で1秒間隔でアニメーション
        self.next = self.start + interval

        self.piece = [id]

        #frame["右"]などの"右"がkey。keyが変わればindexを0に戻す
        self.key = key
        self.previous_key = key
        self.frame_index = 0
        self.frame = {}
        self.change_table = {}

    def add_frame(self,key,f_list): 
        #f_listは最低長さ1以上のリストでアニメーション用のリスト
        if len(f_list) == 1:             #固定画像で要素が1の場合、
            self.frame[key] = f_list     #f_listは[?]と要素1のリストでないといけない
            self.change_table[key] = [0] #次の要素はインデックス0で毎回同じ
#            self.frame[key].append([f[0],0])
        else:
            self.frame[key] = f_list
            l=[]
            for i in range(len(f_list)):
                l.append(i+1)
            l[-1] = 0
            self.change_table[key] = l

    def update(self):
        super().update()

        if self.next <= pyxel.frame_count:
            self.start = pyxel.frame_count
            self.next = self.start + self.interval

            if self.key == self.previous_key:
                self.frame_index = self.change_table[self.key][self.frame_index]
            else:
                self.frame_index = 0
                self.previous_key = self.key                
            self.id = self.frame[self.key][self.frame_index]
            self.u, self.v = self.sp_group.return_uv(self.id)


####====================================

class Game:
    def __init__(self):
        pyxel.init(128,128)
        pyxel.load("sprite.pyxres")
        self.a = AniSprite(0,0,0,0,2,"r",sp4Group)
        self.a.add_frame("r",[0,2,1,3,1,0])
        self.a.speed(256,256)
        pyxel.run(self.update,self.draw)
        
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.a.update()

    def draw(self):
        pyxel.cls(0)
        self.a.draw()


if __name__=="__main__":
    Game()