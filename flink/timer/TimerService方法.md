
Context 和 OnTimerContext 所持有的 TimerService 对象拥有以下方法:

* currentProcessingTime(): Long 返回当前处理时间
* currentWatermark(): Long 返回当前 watermark 的时间戳
* registerProcessingTimeTimer(timestamp: Long): Unit 会注册当前 key 的processing time 的定时器。当 processing time 到达定时时间时，触发 timer。
* registerEventTimeTimer(timestamp: Long): Unit 会注册当前 key 的 event time 定时器。当 水位线大于等于定时器注册的时间时，触发定时器执行回调函数。
* deleteProcessingTimeTimer(timestamp: Long): Unit 删除之前注册处理时间定时器。如果没有这个时间戳的定时器，则不执行。
* deleteEventTimeTimer(timestamp: Long): Unit 删除之前注册的事件时间定时器，如果没有此时间戳的定时器，则不执行。
* 当定时器 timer 触发时，会执行回调函数 onTimer()。注意定时器 timer 只能在keyed streams 上面使用。

