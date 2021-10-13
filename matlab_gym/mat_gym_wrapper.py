import gym
import numpy as np
import matlab
import matlab.engine

class MatlabGymWrapper(gym.core.Env):
    """
    Wraps an exisiting Matlab environment (compatible with the MatlabRLToolbox)
    and exposes it to python

    """
    
    def __init__(self, env_path: str, env_name: str):
        self.eng = matlab.engine.start_matlab()
        self.eng.addpath(env_path)
        self.env = self.eng.eval(env_name)
        self.eng.workspace["matEnv"] = self.env
        self.eng.workspace["obsInfo"] = self.eng.eval("matEnv.getObservationInfo()")

        obs_class = self.eng.eval('class(obsInfo)')
        if 'rlNumericSpec' not in obs_class:
            raise NotImplementedError(f"Currently only supports observations described by rlNumericSpec, got: {obs_class}")

        obs_dtype_str = self.eng.eval("obsInfo.DataType")
        if obs_dtype_str == "double":
            obs_dtype = np.float64
        else:
            raise NotImplementedError(f"Currently do not support observations of type {obs_dtype_str}")

        obs_dim = np.array(self.eng.eval("obsInfo.Dimension"), dtype=int).squeeze()
        obs_lower = np.array(self.eng.eval("obsInfo.LowerLimit")).item()
        obs_upper = np.array(self.eng.eval("obsInfo.UpperLimit")).item()
        self.observation_space = gym.spaces.Box(low=obs_lower, high=obs_upper, shape=obs_dim, dtype=obs_dtype)

        self.eng.workspace["actInfo"] = self.eng.eval("matEnv.getActionInfo()")
        act_class = self.eng.eval('class(actInfo)')
        if 'rlNumericSpec' not in act_class:
            raise NotImplementedError(f"Currently only supports actions described by rlNumericSpec, got: {act_class}")

        act_dtype_str = self.eng.eval("actInfo.DataType")
        if act_dtype_str == "double":
            act_dtype = np.float64
            self.matlab_dtype = matlab.double
        else:
            raise NotImplementedError(f"Currently do not support actions of type {act_dtype_str}")

        act_dim = np.array(self.eng.eval("actInfo.Dimension"), dtype=int).squeeze()
        act_lower = np.array(self.eng.eval("actInfo.LowerLimit")).item()
        act_upper = np.array(self.eng.eval("actInfo.UpperLimit")).item()
        self.action_space = gym.spaces.Box(low=act_lower, high=act_upper, shape=act_dim, dtype=act_dtype)

    def step(self, action: np.ndarray):
        matlab_action = self.matlab_dtype(action.tolist())
        matlab_action.reshape((self.action_space.shape[0],1))
        obs, rew, done, info = self.eng.step(self.env, matlab_action, nargout=4)
        obs = np.array(obs).squeeze()
        return obs, rew, done, info

    def reset(self):
        return np.array(self.eng.reset(self.env)).squeeze()

if __name__ == "__main__":
    from seagul.rl.ars import ARSAgent
    import gym
    from gym import register
    from functools import partial
    from mat_gym_wrapper import MatlabGymWrapper
    
    env_partial = partial(MatlabGymWrapper, "/home/sgillen/work/n_link_arm/bball_1dof_apex/", "bball_1_dof_Env_apex_control")
    
    register("bball_1dof-v0", entry_point=env_partial)
#    env = gym.make('bball_1dof-v0')
#    print(env.reset().shape)
    agent = ARSAgent("bball_1dof-v0", seed=0, n_workers=1)
    agent.learn(500)

    # from seagul.rl.ars import ARSAgent
    # from gym import register
    # from functools import partial

    # env_partial = partial(MatlabGymWrapper, "/home/sgillen/work/n_link_arm/", "bball_1_dof_Env")

    # register("bball_1dof-v0", entry_point=env_partial)
    # #env = gym.make('bball_1dof-v0')
    # # print(env.reset().shape)
    # agent = ARSAgent("bball_1dof-v0", seed=0, n_workers=1)
    # agent.learn(500)

    # #env = MatlabGymWrapper("/home/sgillen/work/n_link_arm/", "bball_1_dof_Env")
