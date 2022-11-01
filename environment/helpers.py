from gym import Env

from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.callbacks import StopTrainingOnRewardThreshold, EvalCallback

import os

def next_available(file_name: str, save_path: str, end: str = "") -> str:
    """
    Finds next available path to save in by incrementing a number on the file name.

    Args:
        file_name (str): The file name to save.
        save_path (str): The path to save to.
        end (str, optional): The file suffix (eg: .zip). Defaults to "".

    Returns:
        str: The full path next free path.
    """

    i = 0
    while os.path.exists(save_path + file_name + str(i) + ".txt"):
        i += 1
    return save_path + file_name + str(i) + end
    

def create_train_model(algo: str, path_to_save: str, total_timesteps: int, env: Env, mlp: bool = False):
    """
    Creates and trains a model.

    Args:
        algo (str): Decides which reinforcement learning algorithm to use.
        path_to_save (str): Directory to save model in.
        total_timesteps (int): Total timesteps to train agent for.
        env (Env): The environment to build the model from.
        mlp (bool): Determines whether the model is a multi-layer perceptron or a convolutional neural network.

    Returns:
        The model used.
    
    Bugs:
        Model overwrites previous one if previous isn't renamed.
    """
    
    #callback_on_best = StopTrainingOnRewardThreshold(reward_threshold=300, verbose=1)
    
    eval_callback = EvalCallback(env, verbose=1, n_eval_episodes=5, best_model_save_path="Environment\\BestModels\\")
    if mlp:
        if algo == "PPO":
            model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="Environment\\Logs\\", gamma=0.99)
        elif algo == "A2C":
            model = A2C('MlpPolicy', env, verbose=1, tensorboard_log="Environment\\Logs\\", gamma=0.99)
        else:
            model = DQN('MlpPolicy', env, verbose=1, tensorboard_log="Environment\\Logs\\", gamma=0.99)
    else:
        if algo == "PPO":
            model = PPO('CnnPolicy', env, verbose=1, tensorboard_log="Environment\\Logs\\", gamma=0.99)
        elif algo == "A2C":
            model = A2C('CnnPolicy', env, verbose=1, tensorboard_log="Environment\\Logs\\", gamma=0.99)
        else:
            model = DQN('CnnPolicy', env, verbose=1, tensorboard_log="Environment\\Logs\\", gamma=0.99)
    model.learn(total_timesteps=total_timesteps, callback=eval_callback, n_eval_episodes=5)
    model.save(path_to_save)
    
    return model  

def load_model(algo: str, path_to_load: str, env: Env):
    """
    Loads model from given directory.

    Args:
        algo (str): Decides which reinforcement learning algorithm to use.
        path_to_load (str): Path to load from.
        env (Env): Environment to use for model.

    Returns:
        The model loaded.
    """
    if algo == "PPO":
        model = PPO.load(path_to_load, env=env)
    elif algo == "A2C":
        model = A2C.load(path_to_load, env=env)
    else:
        model = DQN.load(path_to_load, env=env)
    return model

def test_model(model: PPO, env: Env) -> None:
    """
    Tests model and logs extremely detailed customised logs.

    Args:
        model (A2C): The model to test against.
        env (Env): The environment used for the model.
    """
    
    log_name = "CustomLog"
    custom_log_path = os.path.join('Environment', 'Custom Logs') + "\\"
    full_custom_path = next_available(log_name, custom_log_path, ".txt")

    log_name = "FormalLog"
    formal_log_path = os.path.join('Environment', 'Formal Logs') + "\\"
    full_formal_path = next_available(log_name, formal_log_path, ".txt")
    
    custom_log = open(full_custom_path, 'w')
    formal_log = open(full_formal_path, 'w')
    
    episodes = 10
    for episode in range(1, episodes+1):
        obs = env.reset()
        done = False
        score = 0
        turn = 0
        
        while not done:
            action, _ = model.predict(obs)
            obs, reward, done, info = env.step(action)
            score += reward
            turn += 1
            if turn % 5 == 0:
                exits_taken = info[0]["exits taken"]
                potions = info[0]["potions"]
                enemies = info[0]['enemies']
                custom_log.write(f"!!! Episode: {episode} !!!\n")
                custom_log.write(f"Score: {int(score[0])}\n")
                custom_log.write(f"Turn: {turn}\n")
                
                formal_log.write(f"!!! Episode: {episode} !!!\n")
                formal_log.write(f"Score: {int(score[0])}\n")
                formal_log.write(f"Turn: {turn}\n")
                formal_log.write(f"Exits taken: {exits_taken}\n")
                formal_log.write(f"Potions in map: {potions}\n")
                formal_log.write(f"Enemies in map: {enemies}\n\n\n")
                
                for key in info[0]:
                    if key in ["map", "agent view"]:
                        custom_log.write(f"{key}:\n {info[0][key]}\n")
                    else:
                        custom_log.write(f"{key}: {info[0][key]}\n")
    custom_log.close()
    formal_log.close()