#### 昨日回顾

```
1. HBase分布式的可伸缩的Nosql数据库
2. Master、RegionServer、Region、HLog、Store、MemStore、StoreFile\HFile
3. HBase全分布式
4. HBase shell
- namespace
- ddl
- dml
```

#### 今日任务

```
1. JAVA API 
- namespace
- ddl
- dml
```

#### 一 JAVA API 操作HBase

##### 1 连接到HBase的服务

- 导入依赖

```
<dependency>
    <groupId>org.apache.hbase</groupId>
    <artifactId>hbase-client</artifactId>
    <version>1.2.1</version>
</dependency>
```

- 配置客户端的系统中的hosts

```
192.168.49.100 cdh1
192.168.49.101 cdh2
192.168.49.102 cdh3
192.168.49.103 cdh4
```

- 测试连接HBase的服务

```
@Test
    public void test() throws IOException {
        //1. 创建配置对象，指定zookeeper集群的地址
        Configuration configuration = new Configuration();
        configuration.set("hbase.zookeeper.quorum", "cdh2:2181,cdh3:2181,cdh4:2181");
        //2. 获取连接对象
        HBaseAdmin hBaseAdmin = new HBaseAdmin(configuration);
        //3. 测试
        boolean b = hBaseAdmin.tableExists("t1");
        System.out.println(b);
        //4. 释放资源
        hBaseAdmin.close();
    }
```

##### 2 抽取工具类

```
public class HBaseUtils {
    private final static String KEY = "hbase.zookeeper.quorum";
    private final static String VALUE = "cdh2:2181,cdh3:2181,cdh4:2181";
    private static Configuration configuration;

    static {
        //1. 创建配置对象
        configuration = HBaseConfiguration.create();
        configuration.set(KEY, VALUE);
    }

    public static Admin getAdmin() {
        try {
            Connection connection = ConnectionFactory.createConnection(configuration);
            Admin admin = connection.getAdmin();
            return admin;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    public static void close(Admin admin) {
        try {
            if(admin != null) admin.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

##### 3 写一个测试的模板类

```
public class Demo2_Namespace {

    private HBaseAdmin admin;

    @Before
    public void before() {
       admin = (HBaseAdmin) HBaseUtils.getAdmin();
    }

    @Test
    public void createNamespace() {

    }

    @After
    public void after() {
        HBaseUtils.close(admin);
    }
}
```

##### 4 Namespace的CRUD

```
alter_namespace, 
create_namespace, 
describe_namespace, 
drop_namespace, 
list_namespace, 
list_namespace_tables
```

###### 4.1 list_namespace

```
@Test
public void listNamespace() throws IOException {
    //1. 获取到namespace的数组
    NamespaceDescriptor[] namespaceDescriptors = admin.listNamespaceDescriptors();
    //2. 打印namespace
    for(NamespaceDescriptor namespaceDescriptor : namespaceDescriptors) {
    	System.out.println(namespaceDescriptor.getName());
    }
}
```

###### 4.2 create_namespace

```
@Test
public void createNamespace() throws IOException {
    //1. 创建NamespaceDescriptor
    NamespaceDescriptor ns1Descriptor = NamespaceDescriptor.create("ns1").build();
    ns1Descriptor.setConfiguration("name", "lixi");
    //2. 添加到admin
    admin.createNamespace(ns1Descriptor);
}
```

###### 4.3 list_namespace_tables

```
@Test
public void listNamespaceTables1() throws IOException {
    //1. 查询指定的namespace中有多少表
    TableName[] tableNames = admin.listTableNamesByNamespace("hbase");
    //2. 遍历
    for(TableName tableName:tableNames) {
    	System.out.println(tableName.getNameAsString());
    }
}

@Test
public void listNamespaceTables2() throws IOException {
    //1. 查询指定的namespace中有多少表
    HTableDescriptor[] tableDescriptors = admin.listTableDescriptorsByNamespace("hbase");
    //2. 遍历
    for(HTableDescriptor tableDescriptor:tableDescriptors) {
    	System.out.println(tableDescriptor.getNameAsString());
    }
}
```

###### 4.4 修改namespace

```
@Test
public void alterNamespaceTables() throws IOException {
    //1. 获取到namespace的数组
    NamespaceDescriptor ns1Descriptor = admin.getNamespaceDescriptor("ns1");
    //2. 打印namespace
    ns1Descriptor.setConfiguration("name", "lee");
    //3. 提交修改
    admin.modifyNamespace(ns1Descriptor);
}
```

###### 4.5 删除namespace

```
@Test
public void dropNamespace() throws IOException {
	admin.deleteNamespace("ns1");
}
```

##### 5 Table的CRUD

###### 5.1 建表

```
@Test
public void createTable() throws IOException {
    //1.创建表的表述器对象
    HTableDescriptor tableDescriptor = new HTableDescriptor(TableName.valueOf("t1"));
    //2. 创建列簇的描述器
    HColumnDescriptor familyColumn = new HColumnDescriptor("f1");
    //3.添加列簇
    tableDescriptor.addFamily(familyColumn);
    //4.提交表的描述器从而建表
    admin.createTable(tableDescriptor);
}
```

###### 5.2 查询表中所有列簇

```
@Test
public void listTableColumnFamilies() throws IOException {
    //1. 获取到表的描述器
    HTableDescriptor user_info = admin.getTableDescriptor(TableName.valueOf("user_info"));
    //2. 获取到列簇信息
    HColumnDescriptor[] columnFamilies = user_info.getColumnFamilies();
    //3. 遍历
    for(HColumnDescriptor columnFamily : columnFamilies) {
    	System.out.println(columnFamily.getNameAsString());
    }
}
```

###### 5.3 修改表

```
@Test
public void alterTable1() throws IOException {
    //1. 获取到表的描述器
    TableName tableName = TableName.valueOf("user_info");
    HTableDescriptor user_info = new HTableDescriptor(tableName);
    //2. 获取到列簇信息
    HColumnDescriptor familyColumn1 = new HColumnDescriptor("lixi_info");
    user_info.addFamily(familyColumn1);
    //3. 提交修改
    admin.modifyTable(tableName, user_info);
}

tip: 以上例子，不是很好的修改案例，因为它会将表的列簇都删除，然后再添加新的列簇。因为我们是直接创建的一个新的表的描述器。


@Test
public void alterTable2() throws IOException {
    //1. 获取到表的描述器
    TableName tableName = TableName.valueOf("user_info");
    HTableDescriptor user_info = admin.getTableDescriptor(tableName);
    //2. 获取到列簇信息
    HColumnDescriptor familyColumn1 = new HColumnDescriptor("base_info");
    user_info.addFamily(familyColumn1);
    //3. 提交修改
    admin.modifyTable(tableName, user_info);
}
tip: 正确的修改业务逻辑，应该先将原表的信息查询出来，然后再原表的基础之上进行数据的修改。

```

###### 5.4 删除表中的列簇

```
@Test
public void deleteColumnFamily1() throws IOException {
    //1. 获取到表的描述器
    TableName tableName = TableName.valueOf("user_info");
    HTableDescriptor user_info = admin.getTableDescriptor(tableName);
    //2. 删除列簇
    user_info.removeFamily(Bytes.toBytes("lixi_info"));
    //3. 提交修改
    admin.modifyTable(tableName, user_info);
}

@Test
public void deleteColumnFamily2() throws IOException {
    //1. 获取到表的描述器
    TableName tableName = TableName.valueOf("user_info");
    //2. 提交删除
    admin.deleteColumn(tableName, Bytes.toBytes("rock_info"));
}
```

###### 5.5 修改列簇的属性

```
@Test
public void modifyColumnFamily() throws IOException {
    //1. 获取到表的描述器
    TableName tableName = TableName.valueOf("user_info");
    //2. 列簇
    HColumnDescriptor familyColumn1 = new HColumnDescriptor("base_info");
    //2. 提交删除
    admin.modifyColumn(tableName, familyColumn1);
}
```

###### 5.5 删除表

```
@Test
public void deleteTable() throws IOException {
    //1. 获取到表的描述器
    TableName tableName = TableName.valueOf("user_info");
    //2. 处理表是否失效
    if(!admin.isTableDisabled(tableName)) {
    admin.disableTable(tableName);
    }
    //3. 删除表
    admin.deleteTable(tableName);
}
```

##### 6 Table的DML操作

###### 6.1 HBaseUtils

```
public class HBaseUtils {
    private final static String KEY = "hbase.zookeeper.quorum";
    private final static String VALUE = "cdh2:2181,cdh3:2181,cdh4:2181";
    private static Configuration configuration;

    static {
        //1. 创建配置对象
        configuration = HBaseConfiguration.create();
        configuration.set(KEY, VALUE);
    }

    public static Admin getAdmin() {
        try {
            Connection connection = ConnectionFactory.createConnection(configuration);
            Admin admin = connection.getAdmin();
            return admin;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    public static Table getTable() {
        return getTable("user_info");
    }

    public static Table getTable(String tablename) {
        try {
            Connection connection = ConnectionFactory.createConnection(configuration);
            return connection.getTable(TableName.valueOf(tablename));
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    public static void close(Admin admin) {
        try {
            if(admin != null) admin.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void close(Table table) {
        try {
            if(table != null) table.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void close(Admin admin, Table table) {
        close(admin);
        close(table);
    }
}
```

###### 6.2 Put

```
/**
* put 'ns1:t1', 'r1', 'c1', 'value'
*/
@Test
public void put1() throws IOException {
    //1. 创建Put对象
    Put put = new Put(Bytes.toBytes("001"));
    //2. 添加列数据
    put.addColumn(Bytes.toBytes("base_info"), Bytes.toBytes("name"), Bytes.toBytes("lixi"));
    //3. 插入一条记录
    table.put(put);
}

@Test
public void put2() throws IOException {
    //1. 创建Put对象
    Put put1 = new Put(Bytes.toBytes("002"));
    Put put2 = new Put(Bytes.toBytes("003"));
    //2. 添加列数据
    put1.addColumn(Bytes.toBytes("base_info"), Bytes.toBytes("name"), Bytes.toBytes("lixi"));
    put2.addColumn(Bytes.toBytes("base_info"), Bytes.toBytes("name"), Bytes.toBytes("lixi"));

    List<Put> plist = new ArrayList<>();
    plist.add(put1);
    plist.add(put2);
    //3. 插入一条记录
    table.put(plist);
}
```

###### 6.3 Get

- 通过行键查询指定的列簇的信息

```
@Test
public void get1() throws IOException {
    //1. 创建get对象
    Get get = new Get(Bytes.toBytes("001"));
    //2. 查询数据，返回结果对象
    Result result = table.get(get);
    //3. 查询指定列簇
    NavigableMap<byte[], byte[]> navigableMap = result.getFamilyMap(Bytes.toBytes("base_info"));
    //4. 遍历
    Set<Map.Entry<byte[], byte[]>> entries = navigableMap.entrySet();
    for(Map.Entry<byte[], byte[]> entry : entries) {
    	System.out.println(new String(entry.getKey()) +"--->" + new String(entry.getValue()) );
    }
}
```

- get查询二

```
@Test
public void get2() throws IOException {
//1. 创建get对象
Get get = new Get(Bytes.toBytes("001"));
//2. 查询数据，返回结果对象
Result result = table.get(get);
//3. 获取cell的扫描器
CellScanner cellScanner = result.cellScanner();
//4. 遍历扫描器
while(cellScanner.advance()) {
//5. 获取单词扫描的Cell
    Cell cell = cellScanner.current();
    System.out.println(new String(cell.getFamilyArray(),cell.getFamilyOffset(), cell.getFamilyLength())); // 列簇
    System.out.println(new String(cell.getQualifierArray(), cell.getQualifierOffset(), cell.getQualifierLength())); // 列名
    System.out.println(new String(cell.getValueArray(), cell.getValueOffset(), cell.getValueLength())); // 列值
}
```

- get查询三

```
@Test
public void get3() throws IOException {
    //1. 创建get对象
    Get get = new Get(Bytes.toBytes("001"));
    //2. 查询数据，返回结果对象
    Result result = table.get(get);
    //3. 获取cell的扫描器
    CellScanner cellScanner = result.cellScanner();
    //4. 遍历扫描器
    while(cellScanner.advance()) {
        //5. 获取单词扫描的Cell
        Cell cell = cellScanner.current();
        System.out.println(new String(CellUtil.cloneRow(cell)));
        System.out.println(new String(CellUtil.cloneFamily(cell))); // 列簇
        System.out.println(new String(CellUtil.cloneQualifier(cell))); // 列名
        System.out.println(new String(CellUtil.cloneValue(cell))); // 列值
    }
}
```




