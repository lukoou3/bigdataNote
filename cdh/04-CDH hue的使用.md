# CDH hue的使用

## hdfs
用hdfs登录就进入了hdfs的家目录，hue只是对hadoop做了一层包装(把api变成了页面可视化操作)。

hdfs用户就是cdh中最大的用户，就是hdfs这个用户启动的hdfs进程。

![](assets/markdown-img-paste-20200405212341916.png)

![](assets/markdown-img-paste-20200405212406304.png)

![](assets/markdown-img-paste-20200405212608549.png)

在页面上可以直接新建，重命名，修改小文件的内容(其实就是删除之后在添加，hue不不会修改hadoop的api，只是包装api)。
![](assets/markdown-img-paste-20200405212704449.png)

![](assets/markdown-img-paste-20200405212902599.png)

有中文版
![](assets/markdown-img-paste-20200405214737838.png)

## Job Browser
类似于hadoop yarn的8088

![](assets/markdown-img-paste-2020040521500356.png)

![](assets/markdown-img-paste-20200405215100452.png)


## query
![](assets/markdown-img-paste-20200405215227978.png)

![](assets/markdown-img-paste-20200405215308822.png)

## workflow
包装了oozie可以直接拖拽，比直接用oozie方便好用太多

现在这边编写保存了，就可以在任务那引用了。
 ![](assets/markdown-img-paste-20200405220940111.png)
 
 ![](assets/markdown-img-paste-20200405221031565.png)
 
 ## hive 查询
 在这里可以直接执行hive语句
![](assets/markdown-img-paste-20200405222433536.png)
 
![](assets/markdown-img-paste-20200405222935557.png)
 
![](assets/markdown-img-paste-20200405223010531.png)


![](assets/markdown-img-paste-20200405223445622.png)

![](assets/markdown-img-paste-20200405223422930.png)

![](assets/markdown-img-paste-20200405223516420.png)

![](assets/markdown-img-paste-2020040522381237.png)

可以查看MapReduce的日志，还是比较好用的
![](assets/markdown-img-paste-20200405224016984.png)

![](assets/markdown-img-paste-20200405224210364.png)

![](assets/markdown-img-paste-20200405224226343.png)
 
 ![](assets/markdown-img-paste-2020040522441060.png)
 
 cm中也可以监控到任务的运行：
 ![](assets/markdown-img-paste-20200405224652617.png)
 
 
 