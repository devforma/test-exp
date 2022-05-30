# 文档v0.1

阅读说明：带（TODO）的部分是目前待实现的前端栈



## 目录

Scenario 0：项目结构与获取自定义范围内的交通数据

Scenario 1：运行仿真

Scenario 2：交通信号控制（未完成）

Scenario 3：拥堵定价（未完成）



## Scenario 0：项目结构与获取自定义范围内的交通数据

#### 代码结构

/--
​	/roadnet/：基于路网odps数据生成路网.pkl文件和路网.txt文件
​	/flow/：基于路网.pkl文件生成车流.txt（已提供样例.pkl文件）
​	/run/：基于路网.txt和车流.txt文件进行交通模拟（已提供样例路网和车流文件）
​	/ui/：可视化工具



#### 环境配置

```
	docker pull huangzherui/open-engine:latest
	docker run -v {该文件夹绑定在本地的目录} -it huangzherui/open-engine:latest bash
```


#### 获取路网源数据：

以经纬度范围 (125.1851, 125.4295, 43.7725, 43.9277) 的shanghai地图数据为例，ODPS命令如下：

```
	use nsodps_dev;
	
	drop table shanghai_node_tmp;
    drop table shanghai_edge_tmp1;
    drop table shanghai_edge_tmp2;
    create table shanghai_node_tmp(osmid BIGINT, x FLOAT, y FLOAT);
    create table shanghai_edge_tmp1(osmid BIGINT, osmid_start BIGINT,osmid_end BIGINT);
    create table shanghai_edge_tmp2(osmid BIGINT, highway STRING);
    insert into shanghai_node_tmp select osmid,x,y from osm_node where x>125.1851 and x<125.4295 and y>43.7725 and y<43.9277;
    insert into shanghai_edge_tmp1 select osmid,osmid_start,osmid_end from osm_split_edge where osmid_start in (select osmid from shanghai_node_tmp) and osmid_end in (select osmid from shanghai_node_tmp);
    insert into shanghai_edge_tmp2 select osmid,highway from osm_fulltag_edge where osmid in (select osmid from shanghai_edge_tmp1);
    tunnel download -cn osmid,x,y nsodps_dev.shanghai_node_tmp /workspace/shanghai_node.csv;
    tunnel download -cn osmid,osmid_start,osmid_end nsodps_dev.shanghai_edge_tmp1 /workspace/shanghai_edge1.csv;
    tunnel download -cn osmid,highway nsodps_dev.shanghai_edge_tmp2 /workspace/shanghai_edge2.csv;
```

最终会获得三个.csv文件。



#### 生成路网：

首先将生成的三个.csv文件放在/data/下
接着运行：

```
	python roadnet.py --city shanghai
```

即在/data/目录下生成：

- 简化过后的路网node.csv、edge.csv
- OpenEngine所需的路网文件OpenEngine_roadnet.txt
- 生成车流所需的roadnet.pkl文件


#### 生成车流：/flow/

上一步生成的路网.pkl的文件放在/data/目录下，命名格式为 roadnet_dict_{cityname}.pkl

运行以下命令：

```
	python flow.py --city shanghai
```

输出车流文件在/data/目录下，文件名为CBEngine_0_flow.txt



#### 测试：

将路网.txt文件和车流.txt文件置于/data/目录下

修改配置文件：/data/cfg/shanghai.cfg，将其中的 road_file_addr 与 vehicle_file_addr 重定向为需要运行的车流和路网文件

修改 test.py 中的 roadnet_file，flow_file 与 cfg_file 三个参数，使其指向正确的路网、车流、配置文件

运行以下命令：

```
	python test.py --city shanghai
```



## Scenario 1：运行仿真全流程

参数：

​	--city：当点击前端的cityname控件时，即产生cityname参数。



#### 产生.cfg配置文件（TODO）

产生名为{cityname}.cfg的配置文件，将其放在/data/cfg/目录下。.cfg文件的范例见/data/cfg/nanchang.cfg

其中， road_file_addr 与 vehicle_file_addr 两个key下的value需要重定向为需要运行的车流和路网文件。

#### 准备数据

将路网（roadnet\_{cityname}.txt）和车流（flow\_{cityname}.txt）两个数据文件放在/data/目录下

#### 运行

在/run/目录运行以下命令：

```
	python run_simulation.py --city {cityname}
```

#### 仿真可视化

将/run/log/目录下所有文件复制到/ui/src/log/

在/ui/下运行如下命令

```
	yarn
	yarn start
```

可在local:3000查看可视化结果。

数据范例见/ui/src/log/

#### 数据指标可视化（TODO）

车辆数（vehicle_num）平均速度（avg_speed）在途时间（travel_time）三个数据以字典形式存储在/data/metric/metric_record.json中。读取可进行可视化。

数据范例见/data/metric/metric_record.json




DOCKER

pip3 install osm2gmns requests
