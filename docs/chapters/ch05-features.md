# 第五部分 图像特征与目标识别

## 第五部分：图像特征与目标识别

## 核心问题

经过增强、边缘检测和分割之后，我们希望进一步回答：

图像中有什么？它属于哪一类？目标在哪里？

图像 → 特征表示 → 识别结果

## 图像特征

- 颜色：图像有哪些颜色
- 纹理：局部结构是否重复
- 形状：目标轮廓和几何性质
- 深度特征：由神经网络自动学习

## 目标识别

- 图像分类：整张图是什么
- 目标检测：目标在哪里、是什么
- 图像分割：每个像素属于什么
- 应用：医学、遥感、自动驾驶、工业检测

## 为什么不能直接比较像素？

## 朴素想法

图像本来就是像素矩阵，是否可以直接比较两个图像的像素？

$$
I = \left[ \begin{array}{c c c} I (1, 1) & I (1, 2) & \dots \\ I (2, 1) & I (2, 2) & \dots \\ \vdots & \vdots & \ddots \end{array} \right]
$$

## 像素很敏感

- 目标平移，像素位置改变
- 光照变化，灰度值改变
- 尺度变化，目标大小改变
- 背景复杂，干扰像素很多

## 特征更稳定

- 保留有用信息
- 抑制无关变化
- 方便分类器判断
- 支持相似图像匹配

## 关键理解

## 颜色特征：最直观的图像描述

## 基本思想

颜色特征描述图像中颜色的组成和分布。最常见的方法是颜色直方图：

$$
h (k) = \# \{(x, y) \mid I (x, y) = k \}
$$

## 优点

- 简单直观
- 计算速度快
- 对目标位置变化不太敏感
- 适合颜色差异明显的目标

## 局限

- 不描述空间结构
- 不同物体可能颜色相似
- 容易受光照影响
- 不能区分形状差异

## 例子

只看颜色时，绿色苹果和绿色葡萄可能很难区分。

## 纹理与形状特征

## 纹理特征

纹理描述局部灰度或颜色的重复变化模式。

- 粗糙或平滑
- 是否有周期性
- 是否有方向性
- 局部结构是否规则

## 形状特征

形状描述目标区域的几何外观。

- 面积、周长
- 长宽比
- 圆形度
- 边界轮廓

## 应用理解

- 纹理：木纹、布料、草地、医学组织结构；
- 形状：零件检测、字符识别、病灶轮廓分析。

## 注意

形状特征通常依赖前一步分割结果；分割不准，形状描述也会不可靠。

## 局部特征：图像中的关键位置

## 基本思想

有些位置比普通像素更有辨识度，例如角点、斑点、边缘交汇处和纹理突变处。

## 局部特征关注

- 哪些位置比较稳定
这些位置周围长什么样
- 不同图像中能否找到对应关系

## 典型应用

- 图像匹配
全景拼接
- 目标跟踪
- 三维重建
- 视觉定位

## 一句话

局部特征像图像中的 “指纹点”，可以帮助计算机建立图像之间的对应关系。

## 从人工特征到深度特征

## 传统识别流程

图像 → 人工特征 → 分类器 → 类别

## 深度学习识别流程

图像 → 神经网络 → 类别

## 人工特征

- 可解释性较强
- 设计依赖经验
- 复杂场景表达能力有限

## 深度特征

- 从数据中自动学习
- 表达能力强
- 依赖数据、算力和训练方法

## 卷积神经网络：自动学习图像特征

## 基本思想

卷积神经网络 CNN 可以从大量图像中自动学习多层次特征。

像素 → 边缘 → 纹理 → 部件 → 目标

## 低层特征

- 边缘
- 角点
- 颜色变化

## 中层特征

- 局部纹理
- 轮廓结构
- 目标部件

## 高层特征

- 人脸
- 车辆
- 器官
- 场景语义

## 卷积操作：从滤波到 CNN

## 卷积形式

卷积核在图像上滑动，检测局部区域中是否存在某种模式。

$$
g (i, j) = \sum_ {m, n} w (m, n) f (i - m, j - n)
$$

## 前面讲过的卷积

- 均值滤波：卷积核用于平滑
- Sobel 算子：卷积核用于边缘检测
- 拉普拉斯算子：卷积核用于锐化

## CNN 中的卷积

- 卷积核不是人工指定
- 通过训练数据自动学习
- 不同层学习不同层次的模式

## 重要联系

CNN 中的卷积，与滤波、锐化、边缘检测在数学形式上是相通的。

## 图像分类、目标检测与图像分割

## 图像分类

图像 $\rightarrow$ 类别

- 回答：整张图是什么
- 输出：一个类别
- 例：猫、狗、汽车

## 目标检测

图像 $\rightarrow$ 框 $+$ 类别

- 回答：目标在哪里、是什么
- 输出：边界框和类别
- 例：行人检测

## 图像分割

图像 $\rightarrow$ 像素类别

- 回答：每个像素是什么
- 输出：像素级 mask
- 例：道路分割

## 一句话

分类回答 “是什么”，检测回答 “在哪里、是什么”，分割回答 “每个像素是什么”。

## 代码演示：图像分米

**任务：**

用 CIFAR-10 图像训练一个简单 CNN，输出整张图的类别。

**Python 实现：**

```python
class TinyCifarCNN(nn.Module):
    def __init__(self):
    super().__init__()
    self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
    self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
    self.fc = nn.Linear(64 * 8 * 8, 10)

    def forward(self, x):
    x = F.max_pool2d(F.relu(self.conv1(x)), 2)
    x = F.max_pool2d(F.relu(self.conv2(x)), 2)
    x = x.flatten(1)
    return self.fc(x)
```

<a href="https://mybinder.org/v2/gh/ln2a/IMAGE_ENGINEERING_ECNU/main?urlpath=%2Fdoc%2Ftree%2Fpython-tutorial%2Fex11_ch05.ipynb" target="_blank" style="display: inline-block; background-color: #03a9f4; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-size: 15px; margin-top: 4px; margin-bottom: 8px;">运行此代码 →</a>

\# 输出 logits，经过 softmax 后得到每个类别的概率

**输出形式：**

一张图像 $\longrightarrow$ $[p_{1}, p_{2}, \ldots, p_{10}]$

选择概率最大的类别作为预测结果。

## 代码演示・目标检测

**任务：**

输入一张图像，输出目标类别和边界框。

$$
\text { 图像 } \rightarrow (\mathrm{class}, x _ {1}, y _ {1}, x _ {2}, y _ {2})
$$

**Python 实现：**

```python
class TinyDetector(nn.Module):
    def __init__(self):
    super().__init__()
    self.features = nn.Sequential(
    nn.Conv2d(3,16,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(16,32,3,padding=1), nn.ReLU(), nn.MaxPool2d(2))
    self.shared = nn.Sequential(nn.Flatten(),
    nn.Linear(32*16*16,128), nn.ReLU())
    self.cls_head = nn.Linear(128, 2) # 类别
    self.box_head = nn.Linear(128, 4) # 边界框

def forward(self, x):
    h = self.shared(self.features(x))
    return self.cls_head(h), torch.sigmoid(self.box_head(h))
```

<a href="https://mybinder.org/v2/gh/ln2a/IMAGE_ENGINEERING_ECNU/main?urlpath=%2Fdoc%2Ftree%2Fpython-tutorial%2Fex12_ch05.ipynb" target="_blank" style="display: inline-block; background-color: #03a9f4; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-size: 15px; margin-top: 4px; margin-bottom: 8px;">运行此代码 →</a>

\# 损失 = 分类损失 + 位置框回归损失

## 代码演示・图像分割

**任务：**

输入一张图像，输出一张与原图大小对应的 mask。

图像 $\rightarrow$ 像素级类别图

**Python 实现：**

```python
class TinySegNet(nn.Module):
    def __init__(self):
    super().__init__()
    self.enc1 = nn.Conv2d(3, 16, 3, padding=1)
    self.enc2 = nn.Conv2d(16, 32, 3, padding=1)
    self.dec1 = nn.Conv2d(32, 16, 3, padding=1)
    self.out = nn.Conv2d(16, 1, 1)

def forward(self, x):
    x = F.relu(self.enc1(x))
    x = F.max_pool2d(x, 2)
    x = F.relu(self.enc2(x))
    x = F.interpolate(x, scale_factor=2)
    x = F.relu(self.dec1(x))
    return self.out(x)
```

\# 每个像素输出一个值，sigmoid 后表示属于目标的概率

## Foundation Model: 用 CLIP 提取特征

## 基本思想

CLIP 这类大模型已经在大规模图文数据上学习了通用视觉特征。

图像 → CLIP 图像编码器 → 特征向量 → 线性分类器

## 普通 CNN

- 从当前数据集开始训练
- 小数据时容易过拟合
- 训练成本相对更高

## CLIP 特征

- 复用大模型已有特征
- 只训练简单分类头
- 小样本任务中常常更稳定

## 理解

Foundation model 可以看作一个通用特征提取器，把 “学特征” 的成本提前完成。

## 识别结果如何评价？

## 分类任务常用指标

- Accuracy: 整体预测正确的比例；- Precision：预测为某类的样本中，有多少是真的；
- Recall：真实属于某类的样本中，有多少被找回；
- F1: 综合考虑 Precision 和 Recall。

$$
\text { Accuracy } = \frac {\text { 预测正确的样本数 }}{\text { 总样本数 }}
$$

## 检测和分割常用指标：IoU

$$
\mathrm{IoU} = \frac {\text {预测区域} \cap \text {真实区域}}{\text {预测区域} \cup \text {真实区域}}
$$

## 注意

评价指标要结合任务目标选择，不能只看一个数字。

## 图像特征与目标识别的应用

## 医学图像

- 判断正常 / 异常
- 辅助定位病灶
- 分析病理切片
- 要重视可靠性与临床验证

## 工业检测

- 缺陷识别
- 零件分类
- 表面划痕检测

## 遥感图像

- 建筑、道路、水体识别
- 船只、车辆等小目标检测
- 地物分类和变化检测

## 自动驾驶

- 车辆、行人、交通标志检测
- 道路和车道线分割
- 场景理解与决策辅助

## 第五部分阶段小结

1 图像特征是对图像有用信息的数值化描述。
② 颜色、纹理、形状和局部结构都是常见人工特征。
③ 直接比较像素往往不稳定，需要更稳健的特征表示。
4 传统方法通常先人工设计特征，再使用分类器识别。
5 深度学习方法可以从数据中自动学习多层次特征。
6 图像分类、目标检测和图像分割回答的问题不同。
7 Foundation model 可以作为通用特征提取器，降低小样本任务成本。

## 本部分核心

从 “图像是什么样子” 到 “图像里有什么”，关键在于建立有效的图像表示。

## 结束语

## 图像工程研究什么？

它研究的不只是 “怎样处理一张图片”，而是：

- 图像如何形成；
- 图像如何被表示；
- 图像如何被增强和恢复；
- 图像中的结构如何被提取；
- 图像中的目标如何被理解。

## 一句话总结

图像工程把现实世界中的视觉信息，转化为计算机可以处理、分析和理解的数字信息。

谢谢！
