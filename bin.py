class Grid(MDP):
    def __init__(self,grid,reward_default=-0.04,y=0.9,noise=0.2):
        states = []
        terminals = []
        reward = {}
        rows = len(grid)
        cols = len(grid[0])
        for i in range(rows):
            for j in range(cols):
                content=grid[i][j]
                if content != "*":
                    states.append((i,j))
                    if isinstance(content,(int,float)):
                        reward[(i,j)]=content
                        terminals.append((i,j))
                    else:
                        reward[(i,j)]=reward_default
                        if content=="S":
                            init_state =(i,j)

        super().__init__(states,y)
        self.end_states=terminals
        self.rows = rows
        self.cols = cols
        self.reward=reward
        self.noise=noise
        self.displacements = {"up":[(-1,0),(0,-1),(0,1)],
                                         "down":[(1,0),(0,-1),(0,1)],
                                         "left":[(0,-1),(-1,0),(1,0)],
                                         "right":[(0,1),(-1,0),(1,0)]}
    
    def R(self,state):
        return self.reward[state]
    
    def A(self,state):
        return (["exit"] if state in self.end_states else ["up","down","left","right"])
    
    def T(self,state,action):
        def move(state,m):
            x,y = state
            i,j = m
            nx,ny=x+i,y+j
            if (nx,ny) in self.states:
                return nx,ny
            else:
                return x,y

        if action == "exit":
            return ([(state,0)])
        else:
            mov = self.displacements[action]
            pok = 1-self.noise
            pnook = self.noise/2
            return [(move(state,mov[0]),pok),
                      (move(state,mov[1]),pnook),
                      (move(state,mov[2]),pnook)]
        
        
        
# grid1 = [
#     [' ',' ',' ',+1],
#     [' ','*',' ',-1],
#     [' ',' ',' ',' ']
# ]

#cuad1_MDP=Grid(grid1,y=0.8)

###
# Ejemplo 2
###