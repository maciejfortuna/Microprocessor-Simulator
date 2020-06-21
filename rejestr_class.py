class rejestr:
    def __init__(self):
        self.H = 0
        self.L = 0
        self.preview = None
    
    def update_preview(self):
        self.preview.update(str(self.H),str(self.L))

    def clear_cont(self):
        self.H = 0
        self.L = 0