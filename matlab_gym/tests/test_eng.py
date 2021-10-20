import gym
from gym import register
from functools import partial
from matlab_gym.mat_gym_wrapper import MatlabGymWrapper
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3 import A2C, DDPG, DQN, PPO, SAC, TD3
from stable_baselines3.common.env_util import make_vec_env
import numpy as np
import time
from multiprocessing import Process
import torch

def run_ppo(seed):
    torch.set_num_threads(1)
    algo = 'ppo'
    env_fn = "bball_1_dof_Env_apex_control"
    env_partial = partial(MatlabGymWrapper, "/home/sgillen/work/n_link_arm/", env_fn)
    register("n_link_arm-v0", entry_point = env_partial)

    env = make_vec_env("n_link_arm-v0", n_envs = 1)
    env = VecNormalize(env)

    model = PPO('MlpPolicy',
                env,
                verbose=2,
                seed = int(seed),
                device='cpu',
                policy_kwargs={"net_arch":[64,64]},
                n_steps=2048,
                batch_size=64,
                gae_lambda=0.95,
                gamma=0.99,
                n_epochs=10,
                ent_coef=0.001,
                learning_rate=2.5e-4,
                clip_range=0.2
                )
    model.learn(2e4)

if __name__ == "__main__":
    run_ppo(0)
    print(f"experiment complete, total time: {time.time() - start}")
