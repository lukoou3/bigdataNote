# 调试Local模式下带状态的Flink任务
Flink1.12版可以通过在configuration设置execution.savepoint.path来解决:
```java
ParameterTool tool = ParameterTool.fromArgs(args);
Configuration envCfg = new Configuration();
envCfg.setString("execution.savepoint.path",tool.get("execution.savepoint.path"));
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(envCfg);
```

其他的笨方法：
```
https://blog.csdn.net/shirukai/article/details/106744796
https://blog.csdn.net/u011250186/article/details/108382386
```
