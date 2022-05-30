import os, sys
from wrapper import Wrapper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import citypb

def main():
    roadnet_file = './data/roadnet_nanchang.txt'
    flow_file = './data/flow_nanchang.txt'
    cfg_file = './cfgs/nanchang.cfg'
    wrapper = Wrapper(roadnet_file, flow_file, cfg_file)
    wrapper.test_runtime()
    pass

if __name__ == '__main__':
    main()