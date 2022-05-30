from roadnet.roadnet_simplify import Roadnet_simplify
from roadnet.data_transform import Data_transform
from roadnet.data_input import Data_input
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

# init input data
input_path = './data'
dp_address = ''
city = args.city
longtitude = ''
latitude = ''
inputdata = Data_input(input_path=input_path, dp_address=dp_address, city=city, longtitude=longtitude, latitude=latitude)
# inputdata.from_odps()

# modify here--------------------------------------------------------------------------------------
node_path = input_path + '/nanchang_node.csv' # full path of input node.csv
edge_from_to_path = input_path + '/nanchang_edge1.csv' # full path of input edge_from_to.csv
edge_level_path = input_path + '/nanchang_edge2.csv' # full path of input edge_level.csv
reserved_edge_level_set = {'motorway', 'trunk', 'primary'} # reserved road levels
# --------------------------------------------------------------------------------------------------

output_path = './data' # full path of simplified node.csv and edge.csv and OpenEngine roadnet file

# simplify roadnet
roadnet = Roadnet_simplify(node_path = node_path,
                           edge_from_to_path = edge_from_to_path,
                           edge_level_path= edge_level_path,
                           output_path = output_path,
                           reserved_edge_level_set = reserved_edge_level_set,
                           has_columns = False)
roadnet.simplify_roadnet()

# transform data to OpenEngine format
OpenEngine_roadnet = Data_transform(node_path=output_path + '/node.csv',
                                    edge_path=output_path + '/edge.csv',
                                    directed=True)
OpenEngine_roadnet.OpenEngine_data_transform(output_path=output_path)
OpenEngine_roadnet.Output_roadnet_dict(output_path=output_path)
