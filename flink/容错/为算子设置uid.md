
强烈建议为每个有状态的算子设置uid，因为flink中算子状态的恢复依赖每个算子的uid，只有设置了uid才能保证在代码修改后状态能够恢复。

## 官网的说明
https://ci.apache.org/projects/flink/flink-docs-release-1.13/zh/docs/ops/state/savepoints/

### 分配算子 ID
强烈建议你按照本节所述调整你的程序，以便将来能够升级你的程序。主要通过 uid(String) 方法手动指定算子 ID 。这些 ID 将用于恢复每个算子的状态。

```java
DataStream<String> stream = env.
  // Stateful source (e.g. Kafka) with ID
  .addSource(new StatefulSource())
  .uid("source-id") // ID for the source operator
  .shuffle()
  // Stateful mapper with ID
  .map(new StatefulMapper())
  .uid("mapper-id") // ID for the mapper
  // Stateless printing sink
  .print(); // Auto-generated ID
````

如果不手动指定 ID ，则会自动生成 ID 。只要这些 ID 不变，就可以从 Savepoint 自动恢复。生成的 ID 取决于程序的结构，并且对程序更改很敏感。因此，强烈建议手动分配这些 ID 。

### Savepoint 状态 
你可以将 Savepoint 想象为每个有状态的算子保存一个映射“算子 ID ->状态”:
```
Operator ID | State
------------+------------------------
source-id   | State of StatefulSource
mapper-id   | State of StatefulMapper
```

### F.A.Q
#### 我应该为我作业中的所有算子分配 ID 吗?
根据经验，是的。 严格来说，仅通过 uid 方法给有状态算子分配 ID 就足够了。Savepoint 仅包含这些有状态算子的状态，无状态算子不是 Savepoint 的一部分。

在实践中，建议给所有算子分配 ID，因为 Flink 的一些内置算子（如 Window 算子）也是有状态的，而内置算子是否有状态并不很明显。 如果你完全确定算子是无状态的，则可以跳过 uid 方法。

#### 如果我在作业中添加一个需要状态的新算子，会发生什么？
当你向作业添加新算子时，它将在没有任何状态的情况下进行初始化。 Savepoint 包含每个有状态算子的状态。 无状态算子根本不是 Savepoint 的一部分。 新算子的行为类似于无状态算子。

#### 如果从作业中删除有状态的算子会发生什么? 
默认情况下，从 Savepoint 恢复时将尝试将所有状态分配给新作业。如果有状态算子被删除，则无法从 Savepoint 恢复。

你可以通过使用 run 命令设置 --allowNonRestoredState (简称：-n )来允许删除有状态算子:
```
$ bin/flink run -s :savepointPath -n [:runArgs]
```

#### 如果我在作业中重新排序有状态算子，会发生什么?
如果给这些算子分配了 ID，它们将像往常一样恢复。

如果没有分配 ID ，则有状态操作符自动生成的 ID 很可能在重新排序后发生更改。这将导致你无法从以前的 Savepoint 恢复。

#### 如果我添加、删除或重新排序作业中没有状态的算子，会发生什么?
如果将 ID 分配给有状态操作符，则无状态操作符不会影响 Savepoint 恢复。

如果没有分配 ID ，则有状态操作符自动生成的 ID 很可能在重新排序后发生更改。这将导致你无法从以前的Savepoint 恢复。

#### 当我在恢复时改变程序的并行度时会发生什么? 
如果 Savepoint 是用 Flink >= 1.2.0 触发的，并且没有使用像 Checkpointed 这样的不推荐的状态API，那么你可以简单地从 Savepoint 恢复程序并指定新的并行度。

如果你正在从 Flink < 1.2.0 触发的 Savepoint 恢复，或者使用现在已经废弃的 api，那么你首先必须将作业和 Savepoint 迁移到 Flink >= 1.2.0，然后才能更改并行度。参见升级作业和Flink版本指南。





