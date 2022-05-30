import os, sys
from wrapper.wrapper import Wrapper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import citypb
import argparse

parser = argparse.ArgumentParser(description="OpenEngine Args")
parser.add_argument(
    "--output_path",
    type=str,
    default="./data/log/",
    help="the output dir of the experiment.",
)
args = parser.parse_args()

def main():
    # roadnet_file = './data/roadnet_{}.txt'.format(city)
    # flow_file = './data/flow_{}.txt'.format(city)
    # cfg_file = './data/cfg/{}.cfg'.format(city)
    
    roadnet_file = './data/OpenEngine_roadnet.txt'
    flow_file = './data/CBEngine_0_flow.txt'
    cfg_file = './data/cfg/0_flow.cfg'
    metric_path = './data/metric/'
    # log_path = './data/log/'
    log_path = args.output_path
    wrapper = Wrapper(roadnet_file, flow_file, cfg_file)
    wrapper.run_simulation(log_path, metric_path)
    pass

if __name__ == '__main__':
    main()