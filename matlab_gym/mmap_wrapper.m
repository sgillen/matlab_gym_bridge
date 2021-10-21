classdef mmap_wrapper < handle
    properties
        env
        pid
        recv_mmap
        send_mmap
        send_byte
        recv_byte
        obs_size
        act_size
        
        
        mmapped_file_dir = "./shared_files/"
    end
    
    methods
        function obj = mmap_wrapper(env, pid)
            obj.env = env;
            obj.pid = pid;
            
            send_file_name = obj.mmapped_file_dir + "py_recv_file" + string(pid) + ".dat";
            obj.send_mmap = memmapfile(send_file_name, 'Format', 'double', 'Writable',true);
            
            recv_file_name = obj.mmapped_file_dir + "py_send_file" + string(pid) + ".dat";
            obj.recv_mmap = memmapfile(recv_file_name, 'Format', 'double', 'Writable',false);
            
            obj.send_byte = 1;
            obj.recv_byte = 1;
            
            obj.obs_size = env.getObservationInfo().Dimension(1);
            obj.act_size = env.getActionInfo().Dimension(1);

        end
        
        function obj = runLoop(obj)
            while true
                while obj.recv_mmap.Data(1) ~= obj.recv_byte
                    % do nothing
                end
                obj.recv_byte = mod(obj.recv_byte+1, 2);

            
                if obj.recv_mmap.Data(2) == 1
                    Observation = obj.env.reset();
                    obj.send_mmap.Data(2:obj.obs_size+1) = Observation;
                else
                    Action = obj.recv_mmap.Data(3:end);
                    [Observation, Reward, Done, ~] = obj.env.step(Action);

                    obj.send_mmap.Data(2:obj.obs_size+1) = Observation;
                    obj.send_mmap.Data(1 + obj.obs_size + 1) = Reward;
                    obj.send_mmap.Data(1 + obj.obs_size + 2) = Done;
                end

                obj.send_mmap.Data(1) = obj.send_byte;
                obj.send_byte;
                obj.send_byte = mod(obj.send_byte+1,2);
            end
                    
        end  
    end
end

