# Social-seq-live Client GUI

基于 Social-seq-live 框架，实现两只大鼠社交行为的实时分析，然后根据行为标签，决定是否给予闭环光遗传刺激。这里是  Social-seq-live 的客户端部分，并不包含服务端代码。



![img](assets/social-seq-live-demo.gif)



录制视频推流到服务器；服务器分割识别动物ID，关键点重构，行为识别，得到标签；客户端获取行为标签，判断是否需要执行光遗传刺激。

![img](assets/social-seq-live-pipeline.jpg)



## 安装  Social-seq-live 的客户端

安装  Social-seq-live 的客户端。首先下载代码。

```bash
git clone https://github.com/chenxinfeng4/social-seq-live-client-GUI
cd social-seq-live-client-GUI*
```

然后安装依赖包

```
pip install -r requirement.txt
```



## 运行 客户端软件

进入项目路径，找到 `main.py`.

```bash
python main.py
```



## 简明服务端、客户端的使用教程

参考下面视频。


<video controls>
  <source src="assets/MovieS5_realtime_prediction_240821.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>



## 实时行为分析系统架构

![img](assets/social-seq-live-framework.jpg)



考虑到实验间电脑性能有限，难以流畅运行优化后的模型，本课题采用了云计算的算力。通过以太网络将数据上传到远程的高性能深度学习服务器，利用其更多的GPU资源（4颗NVIDIA RTX3090）。客户端电脑与服务器之间的连接稳定，网络质量高，满足了云计算的网络性能要求。

本课题开发了一套全新的计算架构，包括客户端电脑和服务器两个节点。客户端电脑负责采集视频数据并传输到云服务器，服务器执行动物行为分析流程，并将结果发回客户端电脑。客户端电脑再决定是否给予光遗传刺激。



## 注意

演示视频中使用到了 USV的检测，但实际代码并不提供USV的判断和控制。当前代码只提供基础的关键点姿态行为判断。基于USV的闭环控制仍然在开发中，需要研究人员自行添加逻辑。

