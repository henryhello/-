import random
from time import sleep
import pyglet
from threading import Thread
from MazeGenerator import MazeGenerator
from tk_window import tkWindow
from QLearning import QLearning
from matplotlib import pyplot as plt
from pyglet.window import key
path = ['src']

class MazeTraining(pyglet.window.Window):

    def __init__(self):
        super().__init__(caption="Maze", width=300, height=300)
        self.w = 0
        self.h = 0
        self.wallC = 0
        self.normC = 0
        self.sleep_time = 0.0

        self.obj = tkWindow()
        self.thread1 = Thread(target=self.obj.origin)
        self.thread1.daemon = True
        self.thread1.start()

        self.set_visible(False)

        self.maze_gen = 0
        self.path = 0
        self.start_point = 0
        self.start_index = None
        self.theme = None
        self.sprites = []
        self.agent_sprite = 0
        self.goal_sprite = 0

        self.one_step = 16
        self.wall_tile = 0
        self.normal_tile = 0
        self.yeni = 0
        self.target = None
        self.agent = None

        self.restart = True
        self.acts_done = 0
        self.episodes = 1
        self.puan = []
        self.actions_performed = []

        self.Qobj = 0
        self.alpha = 0
        self.gamma = 0
        self.epsilon = 0
        self.neg_reward = 0
        self.positive_reward = 0
        self.other_reward = 0
        self.n_states = 0
        self.n_actions = 4
        self.states = []
        self.rewards = []
        self.reward_labels = []
        self.q_labels = [0, 0, 0, 0]
        #bunlar ekrana çizmek için kooordinatlarr
        self.çizilen_x = []
        self.çizilen_y = []

        for i in range(self.n_actions):
            self.q_labels[i] = pyglet.text.Label(font_size=10, font_name="Times New Roman")
        self.num = 1

        pyglet.clock.schedule(self.event_loop)
        pyglet.app.run()
        # burda grafik çiziliyor
        if self.obj.end_training_flag:
            self.terminating_sequence()

    def initialize_maze(self):
        self.set_size(self.w, self.h)
        self.set_visible(True)
        self.maze_gen = MazeGenerator(self.w, self.h)
        (self.path, self.start_point) = self.maze_gen.generate_maze()

        self.start_index = self.extract_index([self.obj.maze_baslangic_x, self.obj.maze_baslangic_y], self.states)

        if self.theme == "Retro":
            self.normal_tile = pyglet.resource.image('src/white.png')
            self.wall_tile = pyglet.resource.image('src/black.png')
            self.target = pyglet.resource.image('src/yenitarget.png')
            self.agent = pyglet.resource.image('src/yeniagent.png')
            self.yeni = pyglet.resource.image('src/enkısayol.png')

        self.batch = pyglet.graphics.Batch()
        dosya = open("engel.txt", "w", encoding="utf-8")
        dosya.write("Kırmızı olanlar\n")

        for i in range(0, self.w, 16):
            for k in range(0, self.h, 16):
                if self.path.count([i, k]) == 1:
                    self.sprites.append(pyglet.sprite.Sprite(img=self.normal_tile, x=i, y=k, batch=self.batch))
                else:
                    self.sprites.append(pyglet.sprite.Sprite(img=self.wall_tile, x=i, y=k, batch=self.batch))
                    dosya.write("({},{},K)\n".format(int(i / 16), int(k / 16)))
        dosya.close()

        self.agent_sprite = pyglet.sprite.Sprite(img=self.agent, x=self.obj.maze_baslangic_x, y=self.obj.maze_baslangic_y)
        self.goal_sprite = pyglet.sprite.Sprite(img=self.target, x=self.obj.maze_cikis_x, y=self.obj.maze_cikis_y)

    def initialize_training(self):
        self.other_reward = float(self.obj.var_other)
        self.gamma = float(self.obj.var_gamma)
        self.neg_reward = float(self.obj.var_neg)
        self.positive_reward = float(self.obj.var_pos)

        for i in range(0, self.h, 16):
            for k in range(0, self.w, 16):
                self.states.append([k, i])
                if self.path.count([k, i]) == 1:
                    self.rewards.append(0)
                else:
                    self.rewards.append(self.neg_reward)

        goal_index = self.extract_index([self.goal_sprite.x, self.goal_sprite.y], self.states)
        self.rewards[goal_index] = self.positive_reward

        self.n_states = len(self.states)

        self.label_batch = pyglet.graphics.Batch()

        for i in range(len(self.states)):
            self.reward_labels.append(pyglet.text.Label(str(int(self.rewards[i])), font_name='Times New Roman',
                          font_size=10,x=self.states[i][0]+10, y=self.states[i][1]+15, batch=self.label_batch))

        self.Qobj = QLearning( self.gamma, self.states, self.rewards, self.n_states, self.n_actions)

    @staticmethod
    def extract_index(element, array):
        for i in range(len(array)):
            if array[i][0] == element[0] and array[i][1] == element[1]:
                return i


    def new_possible_state(self, a, x, y):
        if a == 0:
            y += self.one_step
        elif a == 1:
            x += self.one_step
        elif a == 2:
            y -= self.one_step
        elif a == 3:
            x -= self.one_step
        return x, y

    def reset_q_labels(self):

        self.start_index = self.extract_index([self.obj.maze_baslangic_x, self.obj.maze_baslangic_y], self.states)
        value1 = "{:.1f}".format(self.Qobj.QTable[self.start_index][0])
        self.q_labels[0].text = value1
        self.q_labels[0].x = self.agent_sprite.x + 5
        self.q_labels[0].y = self.agent_sprite.y + 60

        value2 = "{:.1f}".format(self.Qobj.QTable[self.start_index][1])
        self.q_labels[1].text = value2
        self.q_labels[1].x = self.agent_sprite.x + 45
        self.q_labels[1].y = self.agent_sprite.y + 15

        value3 = "{:.1f}".format(self.Qobj.QTable[self.start_index][2])
        self.q_labels[2].text = value3
        self.q_labels[2].x = self.agent_sprite.x + 5
        self.q_labels[2].y = self.agent_sprite.y - 25

        value4 = "{:.1f}".format(self.Qobj.QTable[self.start_index][3])
        self.q_labels[3].text = value4
        self.q_labels[3].x = self.agent_sprite.x - 35
        self.q_labels[3].y = self.agent_sprite.y + 15

    def event_loop(self, dt):
        if self.obj.training_flag:
            if self.num == 1:
                self.num += 1
                self.initialize_training()
                self.sleep_time = 0.6
                print("Bölüm", self.episodes)

            if self.restart:
                self.acts_done = 0
                self.agent_sprite.x = self.obj.maze_baslangic_x
                self.agent_sprite.y = self.obj.maze_baslangic_y
                self.reset_q_labels()

                self.restart = False
                return

            old_state = self.extract_index([self.agent_sprite.x, self.agent_sprite.y], self.states)

            y = random.uniform(0, 1)
            if y > self.epsilon:
                act = self.Qobj.max_q_action(old_state)
            else:
                act = random.randint(0, self.n_actions - 1)

            possible_state = self.new_possible_state(act, self.agent_sprite.x, self.agent_sprite.y)
            if possible_state[0] < 0 or possible_state[0] > self.w - self.one_step \
                    or possible_state[1] < 0 or possible_state[1] > self.h - self.one_step:
                return

            self.agent_sprite.x = possible_state[0]
            self.agent_sprite.y = possible_state[1]

            new_state = self.extract_index([self.agent_sprite.x, self.agent_sprite.y], self.states)

            value1 = "{:.1f}".format(self.Qobj.QTable[new_state][0])
            self.q_labels[0].text = value1
            self.q_labels[0].x = self.agent_sprite.x + 5
            self.q_labels[0].y = self.agent_sprite.y + 60

            value2 = "{:.1f}".format(self.Qobj.QTable[new_state][1])
            self.q_labels[1].text = value2
            self.q_labels[1].x = self.agent_sprite.x + 45
            self.q_labels[1].y = self.agent_sprite.y + 15

            value3 = "{:.1f}".format(self.Qobj.QTable[new_state][2])
            self.q_labels[2].text = value3
            self.q_labels[2].x = self.agent_sprite.x + 5
            self.q_labels[2].y = self.agent_sprite.y - 25

            value4 = "{:.1f}".format(self.Qobj.QTable[new_state][3])
            self.q_labels[3].text = value4
            self.q_labels[3].x = self.agent_sprite.x - 35
            self.q_labels[3].y = self.agent_sprite.y + 15

            self.Qobj.update_q_table(old_state, act, new_state)

            self.acts_done += 1
            #en çok tekrarlanan adım sayısı == ise sergilenen aksiyon sayısının sonuncu elemanına
            #yolu tut
            if len(self.actions_performed) != 0:
                if self.actions_performed[int(len(self.actions_performed)) - 1] == self.most_frequent(
                        self.actions_performed):
                    if self.path.count([possible_state[0], possible_state[1]]) == 1:
                        self.çizilen_x.append(possible_state[0])
                        self.çizilen_y.append(possible_state[1])

            if self.rewards[new_state] == self.neg_reward or self.rewards[new_state] == self.positive_reward:
                if self.rewards[new_state] == self.positive_reward:
                    self.puan.append((self.acts_done - 1) * self.other_reward + self.positive_reward)
                    print("In this episode, it reached the goal!")
                else:
                    self.puan.append((self.acts_done - 1) * self.other_reward + self.neg_reward)

                self.episodes += 1
                print('Episode', self.episodes)
                self.actions_performed.append(self.acts_done)
                self.restart = True



        if self.obj.create:
            self.w = self.obj.maze_width * 16
            self.h = self.obj.maze_height * 16
            self.theme = self.obj.color
            self.obj.create = False

            self.initialize_maze()

        if self.obj.back:
            self.set_visible(True)

        if self.obj.regen_flag:
            self.obj.regen_flag = False
            self.initialize_maze()

        if self.obj.dec_flag:
            self.sleep_time += 0.3
            self.obj.dec_flag = False

        if self.obj.inc_flag:
            x = self.sleep_time
            if x - 0.3 < 0:
                self.sleep_time = 0
            else:
                self.sleep_time -= 0.3
            self.obj.inc_flag = False

        if self.obj.redo:
            self.obj.training_flag = False
            self.num = 1
            self.sleep_time = 0.0
            self.restart = True
            self.episodes = 1
            self.acts_done = 0
            self.actions_performed = []
            self.states = []
            self.rewards = []
            self.reward_labels = []
            self.obj.redo = False

        if self.obj.end_training_flag:
            pyglet.clock.unschedule(self.event_loop)

        if self.obj.close_flag:
            #path yolunu çizicem
            #çizdirme buraya gelecek!!!!!
            #self.close()
            '''print("çizilen x: ", self.çizilen_x)
            print("çizilen y: ", self.çizilen_y)
            print("son :", self.actions_performed[int(len(self.actions_performed)) - 1])
            print(self.most_frequent(self.actions_performed))
            print("len x", len(self.çizilen_x))'''

            for i in range(self.most_frequent(self.actions_performed)):
                self.sprites.append(pyglet.sprite.Sprite(img=self.yeni,
                                                         x=self.çizilen_x[len(self.çizilen_x)-self.most_frequent(self.actions_performed)+i],
                                                         y=self.çizilen_y[len(self.çizilen_y)-self.most_frequent(self.actions_performed)+i],
                                                         batch=self.batch))
                '''print("i =", i)
                print("selfler: ", self.çizilen_x[len(self.çizilen_x)-self.most_frequent(self.actions_performed)+i]
                      ,self.çizilen_y[len(self.çizilen_y)-self.most_frequent(self.actions_performed)+i])'''

            pyglet.app.exit()

    def terminating_sequence(self):
        episodes_array = []
        print("收益/成本: ", self.puan, len(self.puan), len(self.actions_performed))
        print("步骤数 : ", self.actions_performed)
        '''print("çizilen x: ", self.çizilen_x)
        print("çizilen y: ", self.çizilen_y)
        print("son :", self.actions_performed[int(len(self.actions_performed)) - 1])
        print(self.most_frequent(self.actions_performed))
        print("len x", len(self.çizilen_x))'''

        for i in range(self.episodes-1):
            episodes_array.append(i+1)

        plt.figure(figsize=(12, 10)).canvas.set_window_title("Graphics")
        plt.subplot(2, 2, 1)
        plt.plot(episodes_array, self.puan)
        plt.title('Episode - Points')
        plt.ylabel('Points')
        plt.xlabel('Episodes')

        plt.subplot(2, 2, 2)
        plt.plot(episodes_array, self.actions_performed)
        plt.title("Episode - Actions per episode")
        plt.ylabel('Actions per episode')
        plt.xlabel('Episodes')


        plt.show()


    def most_frequent(self, List):
        counter = 0
        num = List[0]

        for i in List:
            curr_frequency = List.count(i)
            if (curr_frequency > counter):
                counter = curr_frequency
                num = i

        return num

    def on_draw(self):
        self.clear()

        if len(self.sprites) != 0:
            self.batch.draw()
            self.agent_sprite.draw()
            self.goal_sprite.draw()

        if self.obj.reward_flag:
            self.label_batch.draw()

        if self.obj.q_values_flag:
            self.q_labels[0].draw()
            self.q_labels[1].draw()
            self.q_labels[2].draw()
            self.q_labels[3].draw()

        sleep(self.sleep_time)

        if self.obj.pause_flag:
            while True:
                if not self.obj.pause_flag or self.obj.close_flag or self.obj.redo:
                    break

    def on_close(self):
        self.close()
        pyglet.app.exit()


if __name__ == '__main__':
    MazeTraining()

