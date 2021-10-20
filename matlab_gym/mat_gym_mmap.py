import gym
import numpy as np
import os

import matlab
import matlab.engine

import fastwait


class MatlabGymMmapWrapper(gym.core.Env):
    mmaped_file_dir = "./shared_files"
    
    def __init__(self, env_path, env_fn, train_dtype=np.float64):


        self.train_dtype=train_dtype

        os.makedirs(self.mmaped_file_dir, exist_ok=True)
        self.eng = matlab.engine.start_matlab()
        all_paths = self.eng.genpath(env_path)
        self.eng.addpath(all_paths)
        
        self.eng.workspace["env"] = eval(f"self.eng.{env_fn}(nargout=1)")
        self.eng.workspace["obsInfo"] = self.eng.eval("env.getObservationInfo()")

        obs_class = self.eng.eval('class(obsInfo)')
        if 'rlNumericSpec' not in obs_class:
            raise NotImplementedError(f"Currently only supports observations described by rlNumericSpec, got: {obs_class}")

        obs_dtype_str = self.eng.eval("obsInfo.DataType")
        if obs_dtype_str == "double":
            obs_dtype = np.float64
        else:
            raise NotImplementedError(f"Currently do not support observations of type {obs_dtype_str}")

        obs_dim = (np.array(self.eng.eval("obsInfo.Dimension"), dtype=int).squeeze()[0],)
        print(obs_dim)
        obs_lower = np.array(self.eng.eval("obsInfo.LowerLimit")).item()
        obs_upper = np.array(self.eng.eval("obsInfo.UpperLimit")).item()
        self.observation_space = gym.spaces.Box(low=obs_lower, high=obs_upper, shape=obs_dim, dtype=np.float32)

        self.eng.workspace["actInfo"] = self.eng.eval("env.getActionInfo()")
        act_class = self.eng.eval('class(actInfo)')
        if 'rlNumericSpec' not in act_class:
            raise NotImplementedError(f"Currently only supports actions described by rlNumericSpec, got: {act_class}")

        act_dtype_str = self.eng.eval("actInfo.DataType")
        if act_dtype_str == "double":
            self.act_dtype = np.float64
            self.matlab_dtype = matlab.double
        else:
            raise NotImplementedError(f"Currently do not support actions of type {act_dtype_str}")

        act_dim = (np.array(self.eng.eval("actInfo.Dimension"), dtype=int).squeeze()[0],)
        act_lower = np.array(self.eng.eval("actInfo.LowerLimit")).reshape(act_dim)
        act_upper = np.array(self.eng.eval("actInfo.UpperLimit")).reshape(act_dim)
        self.action_space = gym.spaces.Box(low=act_lower, high=act_upper, shape=act_dim, dtype=np.float32)


        self.obs_size = obs_dim[0]
        self.act_size = act_dim[0]

        pid = os.getpid()
        self.eng.workspace["pythonPid"] = pid


        self.recv_mmap = np.memmap(f"{self.mmaped_file_dir}/py_recv_file{pid}.dat", dtype=np.float64, mode="w+", shape=(1 + self.obs_size + 1 + 1,))
        # self.obs_mmap_arr =  np.memmap(f"{self.mmaped_file_dir}/obs_file{pid}.dat", dtype=obs_dtype, mode='w+', shape=tuple(obs_dim))
        # self.rew_mmap_arr =  np.memmap(f"{self.mmaped_file_dir}/rew_file{pid}.dat", dtype=np.float64, mode='w+', shape=(1,1))
        # self.done_mmap_arr = np.memmap(f"{self.mmaped_file_dir}/done_file{pid}.dat", dtype=bool, mode='w+', shape=(1,1))
        
        self.send_mmap = np.memmap(f"{self.mmaped_file_dir}/py_send_file{pid}.dat", dtype=np.float64, mode='w+', shape=(1+1+self.act_size,))

        self.recv_byte = 1
        self.send_byte = 1

        self.eng.workspace["envRunner"] = self.eng.eval("mmap_wrapper(env, pythonPid)")
        self.eng.eval("envRunner.env.reset()", background=True)
        self.eng.eval("envRunner.runLoop()", background=True)

        #self.eng.eval("envRunner.env.reset()")
        


    def _wait_for_mat(self):

        pointer, read_only_flag = self.recv_mmap.__array_interface__['data']
        fastwait.fastwait(pointer)
        
        # while(self.recv_mmap[0] != self.recv_byte):
        #     pass
        # self.recv_byte = (self.recv_byte + 1) % 2

    def _signal_to_mat(self):
        self.send_mmap[0] = self.send_byte
        self.send_byte = (self.send_byte + 1) % 2



    
    def step(self, act):

        act = act.astype(self.act_dtype)

        self.send_mmap[1] = 0 # 0 -> don't reset
        self.send_mmap[2:] = act

        self._signal_to_mat()
        self._wait_for_mat()
        
        obs = np.array(self.recv_mmap[1:self.obs_size+1], dtype=self.train_dtype)
        rew = np.array(self.recv_mmap[self.obs_size+1], dtype=self.train_dtype)
        done = np.array(self.recv_mmap[self.obs_size+2])

        return obs.squeeze(), rew, done, {}


    def reset(self):
        self.send_mmap[1] = 1; # 1 -> do reset
        self._signal_to_mat()
        self._wait_for_mat()
        
        obs = np.array(self.recv_mmap[1:self.obs_size+1], dtype=self.train_dtype)
        return obs.squeeze()

        

if __name__ == "__main__":
    env = MatlabGymMmapWrapper("/home/sgillen/work/n_link_arm/bball_1dof", "make_env")
    env.step(np.ones(1))
    env.reset()
    env.step(np.ones(1))
        

