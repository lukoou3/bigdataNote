
## Job类
Job类
```java
package org.apache.hadoop.mapreduce;

@InterfaceAudience.Public
@InterfaceStability.Evolving
public class Job extends JobContextImpl implements JobContext {  
  private static final Log LOG = LogFactory.getLog(Job.class);

  @InterfaceStability.Evolving
  public static enum JobState {DEFINE, RUNNING};//job的状态有两种：DEFINE(定义), RUNNING(正在运行)
  private static final long MAX_JOBSTATUS_AGE = 1000 * 2;
  public static final String OUTPUT_FILTER = "mapreduce.client.output.filter";
  /** Key in mapred-*.xml that sets completionPollInvervalMillis */
  public static final String COMPLETION_POLL_INTERVAL_KEY = 
    "mapreduce.client.completion.pollinterval";
  
  /** Default completionPollIntervalMillis is 5000 ms. */
  static final int DEFAULT_COMPLETION_POLL_INTERVAL = 5000;//默认的完成轮询间隔是5秒
  /** Key in mapred-*.xml that sets progMonitorPollIntervalMillis */
  public static final String PROGRESS_MONITOR_POLL_INTERVAL_KEY =
    "mapreduce.client.progressmonitor.pollinterval";
  /** Default progMonitorPollIntervalMillis is 1000 ms. */
  static final int DEFAULT_MONITOR_POLL_INTERVAL = 1000;//默认的监控轮询间隔是1秒

  public static final String USED_GENERIC_PARSER = 
    "mapreduce.client.genericoptionsparser.used";
  public static final String SUBMIT_REPLICATION = 
    "mapreduce.client.submit.file.replication";
  public static final int DEFAULT_SUBMIT_REPLICATION = 10;//作业提交的过程中，会把jar，分片信息，资源信息提交到hdfs的临时目录，默认会有10个复本，多于hdfs默认的副本数，有利于计算节点的本地访问减少网络io

  @InterfaceStability.Evolving
  public static enum TaskStatusFilter { NONE, KILLED, FAILED, SUCCEEDED, ALL }

  static {
    ConfigUtil.loadResources();
  }

  private JobState state = JobState.DEFINE;
  private JobStatus status;
  private long statustime;
  private Cluster cluster;
  private ReservationId reservationId;

}
```

## waitForCompletion()方法
job.waitForCompletion()方法

进入Job类中的waitForCompletion()方法查看，该方法传入一个布尔值参数。方法首先检查Job状态，若处于DEFINE状态则通过submit()方法提交job。而后根据传入的参数决定是否监控并打印job的运行状况。

```java
  /**
   * Submit the job to the cluster and wait for it to finish.
   * @param verbose print the progress to the user
   * @return true if the job succeeded
   * @throws IOException thrown if the communication with the 
   *         <code>JobTracker</code> is lost
   */
  public boolean waitForCompletion(boolean verbose
                                   ) throws IOException, InterruptedException,
                                            ClassNotFoundException {
    //首先检查Job状态，若处于DEFINE状态则通过submit()方法向集群提交job
    //obState.DEFINE 相当于还没有被占用，没有相同的 job 可以继续运行。在后面它提交 job 的时候，它会将这个状态置为JobState.RUNNING(正在运行)                                          
    if (state == JobState.DEFINE) {
      submit();//提交  进入
    }

    //若verbose参数为true，则监控并打印job运行情况
    if (verbose) {
      monitorAndPrintJob();
    } else {
      // get the completion poll interval from the client.
      //从客户端获得完成轮询时间间隔
      int completionPollIntervalMillis = 
        Job.getCompletionPollInterval(cluster.getConf());
      while (!isComplete()) {
        try {
          Thread.sleep(completionPollIntervalMillis);
        } catch (InterruptedException ie) {
        }
      }
    }

    //返回一个boolean值，表示作业是否成功完成
    return isSuccessful();
  }
```
进入方法内部，首先判断的是 state == JobState.DEFINE，才会继续运行。submit() 就是提交 job 的代码，submit() 下面的这些代码主要是用于打印一些完成的信息，如果我们在 WordcountDriver 类里面最后写的提交代码是 job.waitForCompletion(false)  或者 job.submit() 这个时候也不会打印完成的信息。


## submit()方法
该方法负责向集群提交job，方法首先再次检查job的状态，如果不是DEFINE则不能提交作业，setUseNewAPI()方法作用是指定job使用的是新版mapreduce的API，即org.apache.hadoop.mapreduce包下的Mapper和Reducer，而不是老版的mapred包下的类。

submit()中执行了两个比较重要的方法：其一的connect()方法会对Job类中的Cluster类型的成员进行初始化，该成员对象中封装了通过Configuration设置的集群的信息，其内部创建了真正的通信协议对象，它将用于最终的job提交。

getJobSubmitter()方法通过cluster中封装的集群信息(这里是文件系统和客户端)获取JobSubmitter对象，该对象负责最终向集群提交job并返回job的运行进度。最后job提交器对象submitter.submitJobInternal(Job.this, cluster)将当前job对象提交到cluster中，并返回job运行状态给status成员，该方法是JobSubmitter中最核心的功能代码。提交成功后，JobState被设置为RUNNING，表示当前job进入运行阶段，最后控制台中打印跟踪job运行状况的URL。
```java
  /**
   * Submit the job to the cluster and return immediately.
   * @throws IOException
   */
  public void submit() 
         throws IOException, InterruptedException, ClassNotFoundException {
    //再次检查作业的状态
    ensureState(JobState.DEFINE);
    //两套API，这里使用新API
    setUseNewAPI();
    //建立连接
    connect();
    //通过cluster中封装的集群信息(这里是文件系统和客户端)获取JobSubmitter对象，该对象负责最终向集群提交job并返回job的运行进度
    //初始化工作，为cluster赋值，Client即是提交器,分为本体提交器和Yarn提交器，由配置文件决定
    final JobSubmitter submitter = 
        getJobSubmitter(cluster.getFileSystem(), cluster.getClient());
    status = ugi.doAs(new PrivilegedExceptionAction<JobStatus>() {
      public JobStatus run() throws IOException, InterruptedException, 
      ClassNotFoundException {
        return submitter.submitJobInternal(Job.this, cluster);//提交 job 的一些详细信息   （打断点）
      }
    });
    state = JobState.RUNNING;
    LOG.info("The url to track the job: " + getTrackingURL());
   }
```

## submitJobInternal()方法
任务提交器（JobSubmitter）最终提交任务到集群的方法。

首先checkSpecs(job)方法检查作业输出路径是否配置并且是否存在。正确情况是已经配置且不存在，输出路径的配置参数为mapreduce.output.fileoutputformat.outputdir

而后获取job中封装的Configuration对象，添加MAPREDUCE_APPLICATION_FRAMEWORK_PATH（应用框架路径）到分布式缓存中。

通过JobSubmissionFiles中的静态方法getStagingDir()获取作业执行时相关资源的存放路径。默认路径是： /tmp/hadoop-yarn/staging/root/.staging

关于ip地址的方法则是用于获取提交任务的当前主机的IP，并将ip、主机名等相关信息封装进Configuration对象中。

生成jobID并将其设置进job对象中，构造提交job的路径。然后是对该路径设置一系列权限的操作，此处略过不表

writeConf()方法，将Job文件(jar包)上传到任务提交文件夹(HDFS)

（重要）writeSplits()方法，写分片数据文件job.splits和分片元数据文件job.splitmetainfo到任务提交文件夹，计算maptask数量。

submitClient.submitJob()方法，真正的提交作业到集群，并返回作业状态到status成员。submitClient是前面初始化Cluster对象时构建的。

```java
   /**
    Internal method for submitting jobs to the system.

    The job submission process involves:
        Checking the input and output specifications of the job.
        Computing the InputSplits for the job.
        Setup the requisite accounting information for the DistributedCache of the job, if necessary.
        Copying the job's jar and configuration to the map-reduce system directory on the distributed file-system.
        Submitting the job to the JobTracker and optionally monitoring it's status.
    
    Parameters:
        job - the configuration to submit
        cluster - the handle to the Cluster
   */
  JobStatus submitJobInternal(Job job, Cluster cluster) 
  throws ClassNotFoundException, InterruptedException, IOException {

    //validate the jobs output specs 
    //验证作业输出规格，检查作业输出路径是否配置并且是否存在。正确情况是已经配置且不存在
    checkSpecs(job);

    Configuration conf = job.getConfiguration();//获取配置信息
    addMRFrameworkToDistributedCache(conf);//缓存的处理

    //每次提交会创建一个临时路径，一旦提交完就会删除参数的数据 电脑上直接 收拾 tmp 即可找到
    //通过静态方法getStagingDir()获取作业执行时相关资源的存放路径
    //参数未配置时默认是/tmp/hadoop-yarn/staging/提交作业用户名/.staging
    Path jobStagingArea = JobSubmissionFiles.getStagingDir(cluster, conf);
    //configure the command line options correctly on the submitting dfs
    
    //获取提交任务的当前主机的IP，并将ip、主机名等相关信息封装仅Configuration对象中
    InetAddress ip = InetAddress.getLocalHost();
    if (ip != null) {
      submitHostAddress = ip.getHostAddress();
      submitHostName = ip.getHostName();
      conf.set(MRJobConfig.JOB_SUBMITHOST,submitHostName);
      conf.set(MRJobConfig.JOB_SUBMITHOSTADDR,submitHostAddress);
    }

    //生成作业ID,即jobID
    JobID jobId = submitClient.getNewJobID();
    job.setJobID(jobId);
    //构造提交作业路径,jobStagingArea后接/jobID
    Path submitJobDir = new Path(jobStagingArea, jobId.toString());
    JobStatus status = null;
    try {
      //设置一些作业参数
      conf.set(MRJobConfig.USER_NAME,
          UserGroupInformation.getCurrentUser().getShortUserName());
      conf.set("hadoop.http.filter.initializers", 
          "org.apache.hadoop.yarn.server.webproxy.amfilter.AmFilterInitializer");
      conf.set(MRJobConfig.MAPREDUCE_JOB_DIR, submitJobDir.toString());
      LOG.debug("Configuring job " + jobId + " with " + submitJobDir 
          + " as the submit dir");
      // get delegation token for the dir 获得路径的授权令牌,一系列关于作业提交路径权限的设置
      TokenCache.obtainTokensForNamenodes(job.getCredentials(),
          new Path[] { submitJobDir }, conf);
      
      populateTokenCache(conf, job.getCredentials());//获取秘钥和令牌，并将它们存储到令牌缓存TokenCache中

      //这个就是我们为什么要配SSL的免密码登录 这里有用
      // generate a secret to authenticate shuffle transfers
      if (TokenCache.getShuffleSecretKey(job.getCredentials()) == null) {
        KeyGenerator keyGen;
        try {
          keyGen = KeyGenerator.getInstance(SHUFFLE_KEYGEN_ALGORITHM);
          keyGen.init(SHUFFLE_KEY_LENGTH);
        } catch (NoSuchAlgorithmException e) {
          throw new IOException("Error generating shuffle secret key", e);
        }
        SecretKey shuffleKey = keyGen.generateKey();
        TokenCache.setShuffleSecretKey(shuffleKey.getEncoded(),
            job.getCredentials());
      }
      if (CryptoUtils.isEncryptedSpillEnabled(conf)) {
        conf.setInt(MRJobConfig.MR_AM_MAX_ATTEMPTS, 1);
        LOG.warn("Max job attempts set to 1 since encrypted intermediate" +
                "data spill is enabled");
      }

      //复制并配置相关文件
      copyAndConfigureFiles(job, submitJobDir);//提交一些文件的信息  进入 （提前打断点）
      //获取配置文件路径:submitJobDir + "/job.xml"
      Path submitJobFile = JobSubmissionFiles.getJobConfPath(submitJobDir);
      
      // Create the splits for the job
      LOG.debug("Creating splits at " + jtFs.makeQualified(submitJobDir));

      //writeSplits()方法，写分片数据文件job.splits和分片元数据文件job.splitmetainfo,计算map任务数
      //所有的切片信息 提交到 submitJobDir 路径上
      int maps = writeSplits(job, submitJobDir);
      //设置map数,
      conf.setInt(MRJobConfig.NUM_MAPS, maps);
      LOG.info("number of splits:" + maps);

      // write "queue admins of the queue to which job is being submitted"
      // to job file.
      //获取作业队列名queue，取参数mapreduce.job.queuename,默认值为default
      String queue = conf.get(MRJobConfig.QUEUE_NAME,
          JobConf.DEFAULT_QUEUE_NAME);
      AccessControlList acl = submitClient.getQueueAdmins(queue);
      conf.set(toFullPropertyName(queue,
          QueueACL.ADMINISTER_JOBS.getAclName()), acl.getAclString());

      // removing jobtoken referrals before copying the jobconf to HDFS
      // as the tasks don't need this setting, actually they may break
      // because of it if present as the referral will point to a
      // different job.
      TokenCache.cleanUpTokenReferral(conf);//清除缓存的令牌

      if (conf.getBoolean(
          MRJobConfig.JOB_TOKEN_TRACKING_IDS_ENABLED,
          MRJobConfig.DEFAULT_JOB_TOKEN_TRACKING_IDS_ENABLED)) {
        // Add HDFS tracking ids
        ArrayList<String> trackingIds = new ArrayList<String>();
        for (Token<? extends TokenIdentifier> t :
            job.getCredentials().getAllTokens()) {
          trackingIds.add(t.decodeIdentifier().getTrackingId());
        }
        conf.setStrings(MRJobConfig.JOB_TOKEN_TRACKING_IDS,
            trackingIds.toArray(new String[trackingIds.size()]));
      }

      // Set reservation info if it exists
      ReservationId reservationId = job.getReservationId();
      if (reservationId != null) {
        conf.set(MRJobConfig.RESERVATION_ID, reservationId.toString());
      }

      // Write job file to submit dir 写作业文件提交目录
      writeConf(conf, submitJobFile);
      
      //
      // Now, actually submit the job (using the submit name)
      // 现在，实际提交作业（使用提交名称）
      printTokens(jobId, job.getCredentials());
      //通过客户端通信协议ClientProtocol实例submitClient的submitJob()方法提交作业
      //并获取作业状态实例status。由上下文可知，此处的submitClient是YARNRunner或LocalJobRunner
      status = submitClient.submitJob(
          jobId, submitJobDir.toString(), job.getCredentials());
      if (status != null) {
        //作业状态不空，直接返回，否则抛出IOException
        return status;
      } else {
        throw new IOException("Could not launch job");
      }
    } finally {
       //抛出无法加载作业的IOException前，调用文件系统FileSystem实例jtFs的delete()方法，删除作业提交的相关资源目录或者文件submitJobDir
      if (status == null) {
        LOG.info("Cleaning up the staging area " + submitJobDir);
        if (jtFs != null && submitJobDir != null)
          jtFs.delete(submitJobDir, true);

      }
    }
  }
```

## 切片相关方法
### writeSplits()方法
使用newAPI将会调用writeNewSplits()方法
```java
  private int writeSplits(org.apache.hadoop.mapreduce.JobContext job,
      Path jobSubmitDir) throws IOException,
      InterruptedException, ClassNotFoundException {
    JobConf jConf = (JobConf)job.getConfiguration();
    int maps;
    if (jConf.getUseNewMapper()) {
      maps = writeNewSplits(job, jobSubmitDir);
    } else {
      maps = writeOldSplits(jConf, jobSubmitDir);
    }
    return maps;
  }
```

### writeNewSplits()方法

writeNewSplits()方法将会根据我们设置的inputFormat.class通过反射获得inputFormat对象input，然后调用inputFormat对象的getSplits方法，当获得分片信息之后调用JobSplitWriter.createSplitFiles方法将分片的信息写入到submitJobDir/job.split文件中。

数据块：Block是HDFS物理上把数据分成一块一块的。
数据切片：数据切片只是在物理上输入进行分片，并不会在磁盘上将其分成片进行存储。
```java
  @SuppressWarnings("unchecked")
  private <T extends InputSplit>
  int writeNewSplits(JobContext job, Path jobSubmitDir) throws IOException,
      InterruptedException, ClassNotFoundException {
    Configuration conf = job.getConfiguration();
    //反射获取InoutFormat class
    InputFormat<?, ?> input = ReflectionUtils.newInstance(job.getInputFormatClass(), conf);

    //调用inputFormat对象的getSplits方法
    List<InputSplit> splits = input.getSplits(job);
    //集合转数组
    T[] array = (T[]) splits.toArray(new InputSplit[splits.size()]);

    // sort the splits into order based on size, so that the biggest
    // go first
    // 按照大小对切片进行排序，所以大的切片会先被处理
    Arrays.sort(array, new SplitComparator());
    JobSplitWriter.createSplitFiles(jobSubmitDir, conf, 
        jobSubmitDir.getFileSystem(conf), array);
    return array.length;
  }
```

### FileInputFormat类中的getSplits()方法
TextInputFormat继承自FileInputFormat

```java
  /** 
   * Generate the list of files and make them into FileSplits.
   * @param job the job context
   * @throws IOException
   */
  public List<InputSplit> getSplits(JobContext job) throws IOException {
    StopWatch sw = new StopWatch().start();
    //切片的最小值，默认为1。配置参数：mapreduce.input.fileinputformat.split.minsize
    long minSize = Math.max(getFormatMinSplitSize(), getMinSplitSize(job));
    //切片的最大值，默认为Long.MAX_VALUE。配置参数：mapreduce.input.fileinputformat.split.maxsize
    long maxSize = getMaxSplitSize(job);

    // generate splits 切片列表
    List<InputSplit> splits = new ArrayList<InputSplit>();
    //job的输入文件
    List<FileStatus> files = listStatus(job);

    for (FileStatus file: files) {
      Path path = file.getPath();
      long length = file.getLen();//文件的大小，单位为字节
      if (length != 0) {
        BlockLocation[] blkLocations;//文件的块的信息
        if (file instanceof LocatedFileStatus) {
          //本地文件
          blkLocations = ((LocatedFileStatus) file).getBlockLocations();
        } else {
          //非本地文件，从hdfs上获取块信息
          FileSystem fs = path.getFileSystem(job.getConfiguration());
          blkLocations = fs.getFileBlockLocations(file, 0, length);
        }
        //判断是否可切片
        if (isSplitable(job, path)) {
           //获取文件块大小，默认为128M
          long blockSize = file.getBlockSize();
          //计算切片大小，切片大小逻辑由这个方法决定，默认就是blockSize。
          //computeSplitSize方法：return Math.max(minSize, Math.min(maxSize, blockSize));
          long splitSize = computeSplitSize(blockSize, minSize, maxSize);

          //剩余字节数
          long bytesRemaining = length;
          //判断分块中剩余的字节大小与预设分片大小的比例是否超过某个限定值SPLIT_SLOP，该值是一个常量，为1.1，在FileInputFormat类中定义。
          //每次切片时，都要判断切完剩下的部分是否大于块的 1.1 倍
          //也就是说当剩余字节大于预设分片大小的110%后，对剩余的文件继续分片，否则等于或不足110%，直接将剩余文件生成一个分片。
          while (((double) bytesRemaining)/splitSize > SPLIT_SLOP) {
            //计算获取分片的块的索引，只用判断InputSplit的起始位置是否在某个块中。
            //(blkLocations[i].getOffset() <= offset) && (offset < blkLocations[i].getOffset() + blkLocations[i].getLength())
            int blkIndex = getBlockIndex(blkLocations, length-bytesRemaining);
            //制作分片信息，并添加到分片列表。参数：file路径，分片起始位置，分片大小，file块的主机，file块缓存的主机
            splits.add(makeSplit(path, length-bytesRemaining, splitSize,
                        blkLocations[blkIndex].getHosts(),
                        blkLocations[blkIndex].getCachedHosts()));
            //分片的起始位置为0，splitSize，2*splitSize,3*splitSize,...
            bytesRemaining -= splitSize;
          }

          //添加最后一个分片
          if (bytesRemaining != 0) {
            int blkIndex = getBlockIndex(blkLocations, length-bytesRemaining);
            splits.add(makeSplit(path, length-bytesRemaining, bytesRemaining,
                       blkLocations[blkIndex].getHosts(),
                       blkLocations[blkIndex].getCachedHosts()));
          }
        } else { // not splitable
          //不可分片，整个文件作为一个分片
          splits.add(makeSplit(path, 0, length, blkLocations[0].getHosts(),
                      blkLocations[0].getCachedHosts()));
        }
      } else { 
        //Create empty hosts array for zero length files
        //文件长度为0，hosts array 长度为0
        splits.add(makeSplit(path, 0, length, new String[0]));
      }
    }
    // Save the number of input files for metrics/loadgen
    job.getConfiguration().setLong(NUM_INPUT_FILES, files.size());
    sw.stop();
    if (LOG.isDebugEnabled()) {
      LOG.debug("Total # of splits generated by getSplits: " + splits.size()
          + ", TimeTaken: " + sw.now(TimeUnit.MILLISECONDS));
    }
    return splits;
  }
```










```java

```