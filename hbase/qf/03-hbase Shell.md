#### 三 HBase的DDL语法

##### 1 help

```
1. help : 查看所有的hbase的shell命令
2. help 'cmd' : 寻求指定命令的使用方法
e.g. 
help 'create_namespace'
```

##### 2 namespace

###### 2.1 关于namespace的常用命令

```
alter_namespace : 修改命名空间
create_namespace : 创建命名空间
describe_namespace : 查看命名空间的结构
drop_namespace  ： 删除命名空间
list_namespace ：查看HBase中所有的命名空间
list_namespace_tables ：查看指定的命名空间中的所有的表
```

###### 2.2 list_namespace

```
hbase(main):006:0> list_namespace
NAMESPACE
default
hbase
2 row(s) in 0.1090 seconds

hbase(main):014:0> list_namespace '^d'
NAMESPACE
default
```

###### 2.3 create_namespace

```
hbase(main):017:0> create_namespace 'ns1'

hbase(main):018:0> list_namespace
NAMESPACE
default
hbase
ns1
3 row(s) in 0.0680 seconds

hbase(main):022:0> create_namespace 'ns2', {'name'=>'rock'}
```

###### 2.4 describe_namespace

```
hbase(main):021:0> describe_namespace 'ns1'
DESCRIPTION
{NAME => 'ns1'}
1 row(s) in 0.0180 seconds

hbase(main):023:0>  describe_namespace 'ns2'
DESCRIPTION
{NAME => 'ns2', name => 'rock'}
1 row(s) in 0.0030 seconds
```

###### 2.5 alter_namespace

```
hbase(main):024:0> help 'alter_namespace'
修改的namespace的属性！！！

To add/modify a property:

  hbase> alter_namespace 'ns1', {METHOD => 'set', 'PROPERTY_NAME' => 'PROPERTY_VALUE'}

To delete a property:

  hbase> alter_namespace 'ns1', {METHOD => 'unset', NAME=>'PROPERTY_NAME'}

e.g.

hbase(main):025:0> alter_namespace 'ns2', {METHOD => 'set', 'name' => 'lee'}
0 row(s) in 0.0720 seconds

hbase(main):026:0> describe_namespace 'ns2'
DESCRIPTION
{NAME => 'ns2', name => 'lee'}
1 row(s) in 0.0040 seconds

hbase(main):025:0> alter_namespace 'ns2', {METHOD => 'set', 'sex' => 'male'}
0 row(s) in 0.0720 seconds

hbase(main):028:0> describe_namespace 'ns2'
DESCRIPTION
{NAME => 'ns2', name => 'lee', sex => 'male'}
1 row(s) in 0.0070 seconds

hbase(main):029:0> alter_namespace 'ns2', {METHOD => 'unset', NAME => 'sex'}
0 row(s) in 0.0260 seconds

hbase(main):030:0> describe_namespace 'ns2'
DESCRIPTION
{NAME => 'ns2', name => 'lee'}
1 row(s) in 0.0020 seconds
```

###### 2.6 list_namespace_tables

```
hbase(main):044:0> list_namespace_tables 'ns1'
TABLE
t1
1 row(s) in 0.0090 seconds
```

###### 2.7 drop_namespace

```
hbase(main):047:0> drop_namespace 'ns2'
0 row(s) in 0.0490 seconds

hbase(main):048:0> list_namespace
NAMESPACE
default
hbase
ns1
3 row(s) in 0.0990 seconds

tip:这个命令只能删除为空的namespace
```

##### 3 table

###### 3.1 关于表的常见命令

```
create : 建表
alter : 修改表
describe/desc ： 查看表结构
disable/disable_all : 令表失效，在HBase中，只有失效的表才能删除/所有表失效
enable/enable_all ： 使所有的表生效
drop/drop all ： 删除表
exists ： 判断表是否存在
is_disabled/is_enabled ： 是否失效/生效
list ： 查询HBase所有的表
```

###### 3.2 create

```
hbase(main):052:0> create 'ns1:t1', {NAME => 'f1', VERSIONS => 5}
tip:创建一个叫做t1的表，这个表被创建叫做ns1的namespace中，并且列簇叫做f1

hbase(main):053:0> create 't1', {NAME => 'f1'}, {NAME => 'f2'}, {NAME => 'f3'}
hbase(main):054:0> create 'ns1:t1', 'f1', 'f2', 'f3'(这个是我们建表的语法)
tip:上面的两句话表达的意思完全相同。这个t1表被创建在default的namespace中

hbase(main):055:0> create 't1', {NAME => 'f1', VERSIONS => 1, TTL => 2592000, BLOCKCACHE => true}
tip：在default的namespace下创建了table t1。指定列簇f1的属性的配置：VERSIONS,TTL,BLOCKCACHE


hbase(main):056:0> create 'ns1:t2', 'f1', SPLITS => ['10', '20', '30', '40']
0 row(s) in 2.3190 seconds

=> Hbase::Table - ns1:t2
tip: 分片创建表，作用如下图所示：
```

![](003.png)

###### 3.3 list

```
hbase(main):065:0> list
TABLE
ns1:t1
ns1:t2
t1
3 row(s) in 0.0100 seconds

hbase(main):064:0> list 'ns1:.*'
TABLE
ns1:t1
ns1:t2
2 row(s) in 0.0090 seconds
```

###### 3.3 describe/desc

```
hbase(main):068:0> desc 'ns1:t1'
Table ns1:t1 is ENABLED
ns1:t1
COLUMN FAMILIES DESCRIPTION
{NAME => 'f1', BLOOMFILTER => 'ROW', VERSIONS => '5', IN_MEMORY => 'false', KEEP_DELETED_CELLS => 'FALSE', DATA_BLOCK_ENCODING => 'NONE', TTL => 'FOREVER', COMPRESSION => 'NONE', MIN_VERSIONS => '0', BLOCKCACHE => 't
rue', BLOCKSIZE => '65536', REPLICATION_SCOPE => '0'}
1 row(s) in 0.2950 seconds
```

###### 3.4 alter

```
tip:修改添加删除列簇的信息，也可以修改删除添加表的属性。

e.g.修改指定表的指定列簇的属性
hbase(main):071:0> alter 'ns1:t1', NAME => 'f1', VERSIONS => 10
Updating all regions with the new schema...
1/1 regions updated.
Done.
0 row(s) in 1.9450 seconds

hbase(main):068:0> desc 'ns1:t1'


e.g. 修改一张表中的多个列簇的属性
hbase(main):074:0> alter 't1', 'f1', {NAME => 'f2', IN_MEMORY => true}, {NAME => 'f3', VERSIONS => 5}
Updating all regions with the new schema...
1/1 regions updated.
Done.
Updating all regions with the new schema...
1/1 regions updated.
Done.
Updating all regions with the new schema...
1/1 regions updated.
Done.
0 row(s) in 5.6710 seconds

hbase(main):075:0> desc 't1'
Table t1 is ENABLED
t1
COLUMN FAMILIES DESCRIPTION
{NAME => 'f1', BLOOMFILTER => 'ROW', VERSIONS => '5', IN_MEMORY => 'false', KEEP_DELETED_CELLS => 'FALSE', DATA_BLOCK_ENCODING => 'NONE', TTL => 'FOREVER', COMPRESSION => 'NONE', MIN_VERSIONS => '0', BLOCKCACHE => 't
rue', BLOCKSIZE => '65536', REPLICATION_SCOPE => '0'}
{NAME => 'f2', BLOOMFILTER => 'ROW', VERSIONS => '1', IN_MEMORY => 'true', KEEP_DELETED_CELLS => 'FALSE', DATA_BLOCK_ENCODING => 'NONE', TTL => 'FOREVER', COMPRESSION => 'NONE', MIN_VERSIONS => '0', BLOCKCACHE => 'tr
ue', BLOCKSIZE => '65536', REPLICATION_SCOPE => '0'}
{NAME => 'f3', BLOOMFILTER => 'ROW', VERSIONS => '5', IN_MEMORY => 'false', KEEP_DELETED_CELLS => 'FALSE', DATA_BLOCK_ENCODING => 'NONE', TTL => 'FOREVER', COMPRESSION => 'NONE', MIN_VERSIONS => '0', BLOCKCACHE => 't
rue', BLOCKSIZE => '65536', REPLICATION_SCOPE => '0'}
3 row(s) in 0.0300 seconds

e.g. 删除一张表的列簇
hbase(main):078:0> alter 't1', 'delete' => 'f1'
Updating all regions with the new schema...
1/1 regions updated.
Done.
0 row(s) in 2.1780 seconds


e.g. 删除表中的属性
alter 't1', METHOD => 'table_att_unset', NAME => 'coprocessor$1'
```

###### 3.5 exists

```
hbase(main):087:0> exists 't1'
Table t1 does exist
```

###### 3.6 Drop/Enable/Disable

```
hbase(main):095:0> disable 't1'
0 row(s) in 2.2710 seconds

hbase(main):096:0> drop 't1'
0 row(s) in 1.2890 seconds
```

#### 四 HBase的DML语法

##### 1 put命令 ： 只能单行

```
e.g.
hbase(main):101:0> put 'ns1:t1', '001', 'f1:id','1'
- 'ns1:t1' ： 表示 namespace : tablename
- '001' : 表示rowkey
- 'f1:id' ： f1表示列簇:列名
- '1' : 表示的你的列值

e.g.
hbase(main):102:0> put 'ns1:t1', '002', 'f1:id','2',111111111
- 111111111 : 表示的是时间戳

e.g.
put 'ns1:t1', '001', 'f1:name','lixi' 
put 'ns1:t1', '001', 'f1:name','rock'
put 'ns1:t1', '001', 'f1:name','lee'
put 'ns1:t1', '003', 'f1:school','1000phone'
```

##### 2 Scan命令 : 多行查询数据

```
e.g. 查询指定命名空间中的指定的表中的所有的数据

hbase(main):106:0> scan 'ns1:t1'
ROW                                                     COLUMN+CELL
 001                                                    column=f1:id, timestamp=1558021457322, value=1
 001                                                    column=f1:name, timestamp=1558021868579, value=lixi
 002                                                    column=f1:id, timestamp=111111111, value=2

e.g. 查询指定命名空间中的指定表中的指定的列簇中的指定的列
hbase(main):108:0> scan 'ns1:t1', {COLUMNS => 'f1:id'}
ROW                                                     COLUMN+CELL
 001                                                    column=f1:id, timestamp=1558021457322, value=1
 002                                                    column=f1:id, timestamp=111111111, value=2

e.g. 分页查询 ： 
hbase(main):111:0> scan 'ns1:t1', {COLUMNS => ['f1'], LIMIT => 2, STARTROW => '001'}
ROW                                                     COLUMN+CELL
 001                                                    column=f1:id, timestamp=1558021457322, value=1
 001                                                    column=f1:name, timestamp=1558021868579, value=lixi
 002                                                    column=f1:id, timestamp=111111111, value=2
2 row(s) in 0.0200 seconds

e.g. 按时间范围查询数据:起始时间是包含的，结束时间是不包含的
hbase(main):113:0> scan 'ns1:t1', {COLUMNS => 'f1', TIMERANGE => [111111111, 1558021457322]}
ROW                                                     COLUMN+CELL
 002                                                    column=f1:id, timestamp=111111111, value=2
1 row(s) in 0.0170 seconds

e.g. 按照版本查询数据
scan 'ns1:t1', {RAW => true, VERSIONS => 1}

hbase(main):122:0> scan 'ns1:t1', {RAW => true, VERSIONS => 3}
ROW                                                     COLUMN+CELL
 001                                                    column=f1:id, timestamp=1558021457322, value=1
 001                                                    column=f1:name, timestamp=1558022593946, value=lee
 001                                                    column=f1:name, timestamp=1558022542663, value=rock
 001                                                    column=f1:name, timestamp=1558021868579, value=lixi
 002                                                    column=f1:id, timestamp=111111111, value=2
 003                                                    column=f1:school, timestamp=1558022133050, value=1000phone
```

##### 3 Get命令 ： 单行查询

```
e.g. 查询指定表中的行
hbase(main):126:0> get 'ns1:t1', '001'
COLUMN                                                  CELL
 f1:id                                                  timestamp=1558021457322, value=1
 f1:name                                                timestamp=1558022593946, value=lee
2 row(s) in 0.0860 seconds

e.g. 按照时间范围

hbase(main):130:0> get 'ns1:t1', '001', {COLUMNS => 'f1', TIMERANGE => [111111111, 1558021457323]}
COLUMN                                                  CELL
 f1:id                                                  timestamp=1558021457322, value=1
1 row(s) in 0.0040 seconds

e.g. 查询指定列簇
hbase(main):131:0> get 'ns1:t1','001',{COLUMN => 'f1'}
hbase(main):131:0> get 'ns1:t1', '001', 'f1'
COLUMN                                                  CELL
 f1:id                                                  timestamp=1558021457322, value=1
 f1:name                                                timestamp=1558022593946, value=lee
2 row(s) in 0.0100 seconds

e.g. 按版本查
hbase(main):138:0> get 'ns1:t1', '001', {COLUMN => 'f1', VERSIONS => 3}
COLUMN                                                  CELL
 f1:id                                                  timestamp=1558021457322, value=1
 f1:name                                                timestamp=1558022593946, value=lee
 f1:name                                                timestamp=1558022542663, value=rock
 f1:name                                                timestamp=1558021868579, value=lixi
```

##### 4 修改数据/删除数据

###### 4.1 修改数据

```
	没有专门的修改数据的命令，我们使用put命令来修改数据。只要你的表名和列簇以及列名相同，那么后put的数据会覆盖先put的数据。
```

###### 4.2 delete

```
hbase(main):158:0> delete 'ns1:t1', '001', 'f1:name'
```

###### 4.3 count : 统计表中的行数

```
hbase(main):160:0> count 'ns1:t1'
3 row(s) in 0.0710 seconds

=> 3
```

