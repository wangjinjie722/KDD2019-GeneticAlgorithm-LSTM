"""
Sarsa is a online updating method for Reinforcement learning.

Unlike Q learning which is a offline updating method, Sarsa is updating while in the current trajectory.

You will see the sarsa is more coward when punishment is close because it cares about all behaviours,
while q learning is more brave because it only cares about maximum behaviour.
"""

from netsapi.challenge import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#random.seed(197)

class RL(object):
    def __init__(self, action_space, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        self.actions = action_space  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy

        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0]*len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )

    def choose_action(self, observation):
        self.check_state_exist(observation)
        # action selection
        if np.random.rand() < self.epsilon:
            # choose best action
            state_action = self.q_table.loc[observation, :]
            # some actions may have the same value, randomly choose on in these actions
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            # choose random action
            action = np.random.choice(self.actions)
        return action

    def learn(self, *args):
        pass


# backward eligibility traces
class SarsaLambdaTable(RL):
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9, trace_decay=0.9):
        super(SarsaLambdaTable, self).__init__(actions, learning_rate, reward_decay, e_greedy)

        # backward view, eligibility trace.
        self.lambda_ = trace_decay
        self.eligibility_trace = self.q_table.copy()

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            to_be_append = pd.Series(
                    [0] * len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            self.q_table = self.q_table.append(to_be_append)

            # also update eligibility trace
            self.eligibility_trace = self.eligibility_trace.append(to_be_append)

    def learn(self, s, a, r, s_, a_):
        self.check_state_exist(s_)
        q_predict = self.q_table.loc[s, a]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.loc[s_, a_]  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        error = q_target - q_predict

        # increase trace amount for visited state-action pair

        # Method 1:
        # self.eligibility_trace.loc[s, a] += 1

        # Method 2:
        self.eligibility_trace.loc[s, :] *= 0
        self.eligibility_trace.loc[s, a] = 1

        # Q update
        self.q_table += self.lr * error * self.eligibility_trace

        # decay eligibility trace after update
        self.eligibility_trace *= self.gamma*self.lambda_


def generate():
    
    action_space = [[0.0, 0.8], [1.0, 0.0], [0.0, 0.0], [1.0, 1.0]]
    #action_space = [[0.0, 1.0], [1.0, 0.0]]
    rewards_20 = []
    policy_20 = []
    rewards_seq = []
    
    for episode in range(20):
        
        # initial observation
        envSeqDec.reset()
        observation =1
        rewards=0
        policy={}
        
        for j in range(5):

            action = RL.choose_action(str(observation))
            a=action_space[action-1]
            print(';;;;;;;;;;;',j,']]]]',a)
            policy[str(j+1)]=a
            # RL take action and get next observation and reward
            observation_, reward, done, info = envSeqDec.evaluateAction(a)
            if reward:
                rewards+=reward
            if not reward:
                pass
            print(observation_, reward, done, info)
            action_ = RL.choose_action(str(observation_))
            
            # RL learn from this transition
            RL.learn(str(observation), action, reward, str(observation_), action_)
            
            # swap observation
            observation = observation_
            
            # break while loop when end of this episode
            if done:
                print('Episode:', episode + 1, ' Reward: %i' % int(rewards))
                print('Policy:', policy)
                break
                
        rewards_20.append(rewards)
        policy_20.append(policy)
        
    print('Best Reward:',np.max(rewards_20))
    print('Best Policy:',policy_20[np.argmax(rewards_20)])
    x = list(range(len(rewards_20)))
    plt.plot(x, rewards_20)
    #plt.title(f'Sarsa Result action_space: {action_space} learn_rate: {learning_rate} reward_decay: {reward_decay} e_greedy: {e_greedy}')
    plt.title('Sarsa Lamda Result')
    plt.xlabel('Episodes')
    plt.ylabel('Rewards')
    plt.show()



if __name__ == "__main__":
    action_space = [[0.0, 0.8], [1.0, 0.0], [0.0, 0.0], [1.0, 1.0]]
    envSeqDec = ChallengeSeqDecEnvironment(experimentCount=20000)
    action_space = [1,2] # Using two actions can get steady 490 - 500 result.
    RL = SarsaLambdaTable(actions=action_space,
                learning_rate=0.005,
                reward_decay=0.3,
                e_greedy=0.9)
    generate()
