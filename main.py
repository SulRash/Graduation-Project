from stable_baselines3.common.vec_env import DummyVecEnv

import os

import torch
import tensorflow as tf
from src.game import Game
from environment.environment import RLEnv
from environment.helpers import next_available, create_train_model, load_model, test_model

def main():
    mode = int(input("Agent or Game mode? (0 for agent, 1 for game)\n"))
    
    if int(input("Do you want to add a seed? (0 for no, 1 for yes)\n")):
        seed = int(input("Please write the seed down as an integer. Best to make it more than 5 Digits.\n"))
        fixed_seed = True
    else:
        seed = 0
        fixed_seed = False
    
    if mode:
        game = Game(seed=seed, fixed_seed=fixed_seed)
        game.start()
    
    else:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        
        if int(input("Perfect information for the agent? (0 for no, 1 for yes)\n")):
            perfect_info = True
        else:
            perfect_info = False
            
        if int(input("Display game as image or numbers array to agent? (0 for image, 1 for numbers array)\n")):
            to_image = False
        else:
            to_image = True
        
        env = RLEnv(seed=seed, to_image=to_image, fixed_seed=fixed_seed, perfect_info=perfect_info)
        env = DummyVecEnv([lambda: env])
        mode = int(input("Create new model or load existing? (0 for new, 1 for load)\n"))
        
        algo_num = int(input("Which algorithm to use? (0 for DQN, 1 for PPO, 2 for A2C)\n"))
        
        if algo_num == 1:
            algo = "PPO"
        elif algo_num == 2:
            algo = "A2C"
        else:
            algo = "DQN"
        
        if mode:
            path = input("Please write out the path of what to load.\n")
            model = load_model(algo, path, env)
        
        else:
            save_path = os.path.join('Environment', 'SavedModels') + "\\"
            full_path = next_available("", save_path)

            timesteps = int(input("Please enter desired training timesteps.\n"))
            
            if fixed_seed == True:
                env.env_method("set_seed", seed=seed)
            
            if int(input("Multi-layer perceptron or convolutional neural network? (0 for mlp, 1 for cnn)\n")):
                mlp = False
            else:
                mlp = True
                
            print("Creating and training new model...")
            model = create_train_model(algo, full_path, timesteps, env, mlp=mlp)
            
        mode = int(input("Do you wish to test agent? (0 for no, 1 for yes)\n"))
        
        if mode:
            test_model(model, env)
        
        else:
            exit()     

if __name__ == '__main__':
    main()