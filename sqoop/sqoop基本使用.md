## 一、导入数据
在 Sqoop 中，“导入”概念指：从非大数据集群（RDBMS）向大数据集群（HDFS，HIVE，HBASE）中传输数据，叫做：导入，即使用 import 关键字。

### RDBMS 到 HDFS
在 Mysql 中新建一张表并插入一些数据:
```sql
create database testdb; 
use testdb; 
create table user( 
id int not null auto_increment, 
account varchar(255) default null, 
password varchar(255) default null, 
primary key(id) 
); 
 
insert into user(account, password) values('aaa', '123'); 
insert into user(account, password) values('bbb', '123'); 
insert into user(account, password) values('ccc', '123'); 
insert into user(account, password) values('ddd', '123'); 
insert into user(account, password) values('eee', '123'); 
insert into user(account, password) values('fff', '123'); 
insert into user(account, password) values('ggg', '123'); 
insert into user(account, password) values('hhh', '123');
```

导入数据：
#### 全部导入
```
sqoop import \
--connect jdbc:mysql://hadoop01:3306/testdb \
--username root \
--password 123456 \
--table user \
--target-dir /sqoop/import/user \
--delete-target-dir \
--num-mappers 1 \
--fields-terminated-by '\t'
```

#### columns指定导入的字段
注：--columns account,password字段之间不能有空格
```
sqoop import \
--connect jdbc:mysql://hadoop01:3306/testdb \
--username root \
--password 123456 \
--table user \
--columns account,password \
--target-dir /sqoop/import/user \
--delete-target-dir \
--num-mappers 1 \
--fields-terminated-by ','
```
**尖叫提示：columns 中如果涉及到多列，用逗号分隔，分隔时不要添加空格**

#### query选项实现查询导入
query, where子句必须有$CONDITIONS(固定写法)
```
sqoop import \
--connect jdbc:mysql://hadoop01:3306/testdb \
--username root \
--password 123456 \
--query 'select account,password from user where account="ddd" and $CONDITIONS' \
--target-dir /sqoop/import/user \
--delete-target-dir \
--num-mappers 1 \
--fields-terminated-by '\t'
```
尖叫提示：must contain '$CONDITIONS' in WHERE clause.  
尖叫提示：如果 query 后使用的是双引号，则$CONDITIONS  前必须加转移符，防止 shell识别为自己的变量。  
尖叫提示：--query 选项，不能同时与--table 选项使用  

#### where选项实现查询导入
```
sqoop import \
--connect jdbc:mysql://hadoop01:3306/testdb \
--username root \
--password 123456 \
--table user \
--where 'id > 5 and account like "f%"' \
--target-dir /sqoop/import/user_where \
--delete-target-dir \
--num-mappers 1 \
--fields-terminated-by '\t'
```

### RDBMS 到 Hive
hive的database要提前创建：
···
hive -e "create database testdb"
···

导出到hive：
```
sqoop import \
--connect jdbc:mysql://hadoop01:3306/testdb \
--username root \
--password 123456 \
--table user \
--hive-import \
--hive-database testdb \
--hive-table user_to_hive \
--hive-overwrite \
--num-mappers 1 \
--fields-terminated-by '\t'
```
尖叫提示：该过程分为两步，第一步将数据导入到 HDFS，第二步将导入到 HDFS 的数据迁移到 Hive 仓库

尖叫提示：第一步默认的临时目录是/user/admin(用户名)/表名


## 导出数据
在 Sqoop 中，“导出”概念指：从大数据集群（HDFS，HIVE，HBASE）向非大数据集群（RDBMS）中传输数据，叫做：导出，即使用 export 关键字。

### HIVE/HDFS 到 RDBMS
创建mysql中的表
```sql
create table user_from_hive like user;
```

导出数据到MySql
```
sqoop export \
--connect jdbc:mysql://hadoop01:3306/testdb \
--username root \
--password 123456 \
--table user_from_hive \
--export-dir /user/hive/warehouse/testdb.db/user_to_hive \
--input-fields-terminated-by '\t' \
--num-mappers 1
```

```
sqoop export \
--connect jdbc:mysql://hadoop01:3306/testdb \
--username root \
--password 123456 \
--table user_from_hive \
--export-dir /sqoop/import/user_where \
--input-fields-terminated-by '\t' \
--num-mappers 1
```

多次导出会一直显示：map 100% reduce 0%
是因为mysql的主键冲突了，清空表中的数据后，任务才会运行完。
