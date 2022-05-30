from src.roadnet_simplify import Roadnet_simplify
from src.data_transform import Data_transform
from src.data_input import Data_input

# 首先使用cd命令来到工作目录。 Use "cd" command to the context first.

# init input data
input_path = './input_data'
dp_address = ''
city = ''
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

output_path = './output' # full path of simplified node.csv and edge.csv and OpenEngine roadnet file

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
