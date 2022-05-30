from flow.trafficGenerator import Traffic_generator
import argparse

# parse args
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
    main_folder = "./data/"
    output_folder = "./data/"
    city = args.city
    bbox = {'north': 30.2601,  'south': 30.2415, 'east': 120.1828, 'west':  120.1536}
    traffic_duration = 3600
    numveh = 200000
    
    generator = Traffic_generator(city, main_folder, output_folder, bbox, numveh, traffic_duration=traffic_duration)
    generator.initialize(cpus=4)

if __name__ == '__main__':
    main()