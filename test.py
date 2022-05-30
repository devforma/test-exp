import os, sys
from wrapper.wrapper import Wrapper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import citypb
import argparse

parser = argparse.ArgumentParser(description="OpenEngine Args")
parser.add_argument(
    "--city",
    type=str,
    default="nanchang",
    choices=["nanchang"],
    help="the name of the city that serves as simulation base.",
)
args = parser.parse_args()

def main():
    city = args.city
    # roadnet_file = './data/roadnet_{}.txt'.format(city)
    # flow_file = './data/flow_{}.txt'.format(city)
    # cfg_file = './data/cfg/{}.cfg'.format(city)
    roadnet_file = './data/OpenEngine_roadnet.txt'
    flow_file = './data/CBEngine_0_flow.txt'
    cfg_file = './data/cfg/0_flow.cfg'
    wrapper = Wrapper(roadnet_file, flow_file, cfg_file)
    wrapper.test_runtime()
    pass

if __name__ == '__main__':
    main()