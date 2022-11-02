from tkinter import Tk, Canvas, Frame, BOTH, W



class Preview(Frame):
 
    def __init__(self, debug_info):
        super().__init__()
        self.initUI(debug_info)
 
    def initUI(self, debug_info):

        self.master.title("Preview")
        self.pack(fill=BOTH, expand=1)
 
        canvas = Canvas(self)


        for rect in debug_info['forb_area']:
            x0 = rect['x0']/2+500
            x1 = rect['x1']/2+500
            y0 = rect['y0']/2+100
            y1 = rect['y1']/2+100
            canvas.create_rectangle(
            x0, y0, x1, y1,
            outline='black'
            )
            
        for block in debug_info['diagram']['blocks']:
            x = block['x']/2+470
            y = block['y']/2+100
            canvas.create_text(
                x, y, anchor=W, font="DejavuSansLight 8",
                text=block['code'].split('\n')[0]
            )
        
 
        canvas.pack(fill=BOTH, expand=1)
 
    
    @staticmethod
    def draw(debug_info):
        root = Tk()
        ex = Preview(debug_info)
        root.geometry("960x800+300+300")
        root.mainloop()
 
