from trafficGenerator import Traffic_generator

def main():
    main_folder = "./data/"
    output_folder = './output/'
    city = "shenzhen"
    bbox = {'north': 30.2601,  'south': 30.2415, 'east': 120.1828, 'west':  120.1536}
    traffic_duration = 3600
    numveh = 200000
    
    generator = Traffic_generator(city, main_folder, output_folder, bbox, numveh, traffic_duration=traffic_duration)
    generator.initialize(cpus=4)

if __name__ == '__main__':
    main()