from PIL import Image, ImageDraw, ImageFont

class ScheduleImage:

    def __init__(self, days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]):

        self.w_padding = 25

        img = Image.new("RGB", (900+self.w_padding*2, 700), 5330520)


        draw = ImageDraw.Draw(img)

        hsize = 14

        self.hsize = hsize

        sh = int(img.size[1]/hsize)
        sw = int((img.size[0]-(self.w_padding*2))/len(days))

        self.W = img.size[0]-self.w_padding*2
        self.H = img.size[1]

        self.sw = sw
        self.sh = sh

        self.draw = draw

        self.generate_lines()

        self.get_tile = lambda x, y: (sw*x + self.w_padding*2, sh*y)
        self.get_tile_center = lambda x, y: (sw*x+int(sw/2) + self.w_padding*2, sh*y+int(sh/2))

        self.size = (len(days), hsize)

        self.days = days

        self.fnt = ImageFont.truetype("Blink.otf", 20)

        self.add_week_days()
        
        #self.add_tile_coordinates()

        self.img = img

    def generate_lines(self):
        for i in range(self.sh, self.H, self.sh):

            self.draw.line((0, i) + (self.W + self.w_padding*2, i), fill=11053483, width=2)

        for i in range(0, self.W, self.sw):

            self.draw.line((i + self.w_padding*2, 0) + (i + self.w_padding*2, self.H), fill=11053483, width=2)

    def add_week_days(self):
        for i in range(len(self.days)):
            x, y = self.get_tile_center(i, 0)
            _, _, w, h = self.draw.textbbox((0, 0), self.days[i], font=self.fnt)
            self.draw.text((x - w/2, y - h/2), self.days[i], font=self.fnt, fill=(255, 255, 255))

    def add_tile_coordinates(self):
        for i in range(self.size[0]):
            for j in range(1, self.size[1]):
                txt = f"({i}, {j})"
                x, y = self.get_tile_center(i, j)
                _, _, w, h = self.draw.textbbox((0, 0), txt, font=self.fnt)
                self.draw.text((x - w/2, y - h/2), txt, font=self.fnt, fill=(255, 255, 255))

    def schedule(self, data):
        # data should be [(name, start_hour(24h), start_minute, end_hour(24h), end_minute, daydat)]
        end_hour = sorted(data, key=lambda x: x[3], reverse=True)[0][3] + 1
        start_hour = sorted(data, key=lambda x: x[1], reverse=False)[0][1] - 1
        if end_hour - start_hour < self.hsize-1:
            ss = 1
        else:
            ss = 2

        self.draw_time(start_hour, ss)

        self.draw_schedule(start_hour, data)

    def draw_schedule(self, start_hour, data):
        for el in data:
            thisr = el[1] - start_hour
            sx, sy  = self.get_tile(el[5], thisr)
            sy += self.sh* int(el[2]/60) 
            thise = el[4] - start_hour
            ex, ey = self.get_tile(el[5], thise)
            ey += self.sh* int(el[4]/60)
            
            self.draw.rounded_rectangle((sx+5, sy+5, ex+self.sw-3, ey-3), fill=(45, 45, 45), width=0)

            self.write_to_tile(el[5], thisr, el[0])


    def write_to_tile(self, i, j, txt):
        x, y = self.get_tile_center(i, j)
        self.write_to_coords(x, y, txt)

    def write_to_coords(self, x, y, txt):
        _, _, w, h = self.draw.textbbox((0, 0), txt, font=self.fnt)
        self.draw.text((x - w/2, y - h/2), txt, font=self.fnt, fill=(255, 255, 255))

    def draw_time(self, start_hour, ss):
        c = start_hour
        for i in range(1, self.hsize):
            txt = f"{str(c) + ' AM' if c <= 12 else str(c-12) + ' PM'}"
            _, y = self.get_tile_center(0, i)
            _, _, w, h = self.draw.textbbox((0, 0), txt, font=self.fnt)
            self.draw.text((0+self.w_padding - w/2, y - h/2), txt, font=self.fnt, fill=(255, 255, 255))
            c+=ss

    def save(self, out="out.png"):
        self.img.save(out)