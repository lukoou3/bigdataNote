# Impala Shell命令

## Impala Shell概览

### Impala 外部shell
不进入Impala内部，直接执行的ImpalaShell
```
例如：
$ impala-shell -h   -- 通过外部Shell查看Impala帮助
$ impala-shell -p select count(*) from t_stu   -- 显示一个SQL语句的执行计划
```

下面是Impala的外部Shell的一些参数：
```
-h （--help） 帮助
-v （--version） 查询版本信息
-V （--verbose） 启用详细输出
--quiet 关闭详细输出
-p 显示执行计划
-i hostname （--impalad=hostname） 指定连接主机格式hostname：port 默认端口21000, impalad shell 默认连接本机impalad
- r（--refresh_after_connect）刷新所有元数据
-q query （--query=query） 从命令行执行查询，不进入impala-shell

-d default_db （--database=default_db） 指定数据库
-B（--delimited）去格式化输出
--output_delimiter=character 指定分隔符
--print_header 打印列名

-f query_file（--query_file=query_file）执行查询文件，以分号分隔
-o filename （--output_file filename） 结果输出到指定文件
-c 查询执行失败时继续执行

-k （--kerberos） 使用kerberos安全加密方式运行impala-shell
-l 启用LDAP认证
-u 启用LDAP时，指定用户名
```


### Impala内部Shell
```
# impala shell进入
# 普通连接 
impala-shell 


# impala shell命令

# 查看impala版本
select version;

# 特殊数据库
# default，建立的没有指定任何数据库的新表
# _impala_builtins，用于保存所有内置函数的系统数据库

# 库操作
# 创建 
create database tpc;
# 展示
show databases;
# 展示库名中含有指定(格式)字符串的库展示
# 进入
use tpc;
# 当前所在库
select current_database();

#表操作
# 展示(默认default库的表)
show tables;
# 指定库的表展示
show tables in tpc;
# 展示指定库中表名中含有指定字符串的表展示
show tables in tpc like 'customer*';
# 表结构
describe city; 或 desc city;
# select insert create alter

# 表导到另一个库中(tcp:city->d1:city)
alter table city rename to d1.city

# 列是否包含null值
select count(*) from city where c_email_address is null

# hive中 create、drop、alter,切换到impala-shell中需要如下操作
invalidate metadata
# hive中 load、insert、change表中数据(直接hdfs命令操作),切换到impala-shell中需要如下操作
refresh table_name
```














```

```