# 第二部分 图像增强与滤波

## 第二部分：图像增强与滤波

核心问题

现实图像往往存在噪声、模糊、低对比度、光照不均等问题。图像增强与滤波的目标，是让图像更适合观察、分析和后续算法处理。

低质量图像 $\longrightarrow$ 增强后的图像 $\longrightarrow$ 后续分析

- 让暗图变亮；
- 让模糊边缘更清楚；
- 去除噪声干扰；
- 提高目标与背景的差异。

注意

图像增强不一定追求 “真实”，而是追求 “更有用”。

## 什么是图像增强？

定义

图像增强是指通过一定的变换方法，改善图像的视觉效果或突出其中有用信息。

视觉层面

- 看得更清楚
- 对比度更明显
- 细节更容易观察
- 暗部或亮部信息更突出

算法层面

- 便于边缘检测
- 便于目标分割
- 便于特征提取
- 提高后续识别效果

一句话

图像增强是图像理解之前的重要预处理步骤。

## 图像增强的基本类型

常见方法

图像增强方法大致可以分为两类：点运算和邻域运算。

点运算

- 每个像素独立变化
- 不考虑周围像素
例如：亮度调整、对比度调整、灰度变换

$$
g (x, y) = T (f (x, y))
$$

邻域运算

- 当前像素由周围像素共同决定
- 考虑局部结构
例如：平滑滤波、锐化滤波、边缘增强

$$
g (x, y) = T (\Omega_ {x, y})
$$

## 灰度变换：最简单的图像增强

基本思想

对每个像素的灰度值进行函数变换：

$$
s = T (r)
$$

- $r$ : 原始灰度值；- $s$ : 变换后的灰度值；- $T$ : 灰度变换函数。

常见灰度变换

- 线性变换：调整亮度和对比度；
- 对数变换：增强暗部细节；
- Gamma 变换：模拟显示设备和视觉感知；
- 反色变换：突出特殊结构。

## 线性灰度变换

基本形式

$$
s = a r + b
$$

- $a$ 控制对比度；
- $b$ 控制整体亮度；
- $a &gt; 1$ ：增强对比度；
- $0 &lt; a &lt; 1$ ：降低对比度；
- $b &gt; 0$ ：整体变亮；
- $b &lt; 0$ ：整体变暗。

工程理解

很多手机修图软件中的 “亮度” 和 “对比度” 调节，本质上就是灰度变换。

## 直方图：观察灰度分布

什么是直方图？

图像直方图统计每个灰度值在图像中出现的次数。

$$
h (k) = \# \{(x, y) \mid f (x, y) = k \}
$$

- 横轴：灰度值；
- 纵轴：像素数量；
- 暗图像：灰度集中在低值区域；
- 亮图像：灰度集中在高值区域；
- 低对比度图像：灰度分布范围较窄。

关键作用

直方图可以帮助我们判断图像是偏暗、偏亮，还是对比度不足。

## 直方图均衡化

基本思想

把原来集中在某些灰度范围内的像素，重新分布到更宽的灰度范围中，从而增强图像对比度。

$$
s = T (r)
$$

其中 T 由灰度累计分布函数决定。

效果

- 低对比度图像会变得更清晰；
- 暗部和亮部细节可能更加明显；
- 但也可能放大噪声；
- 对某些图像可能产生过增强。

## 图像滤波：利用邻域信息

基本思想

滤波不是只改变一个像素本身，而是根据它周围一小片区域的信息来决定新的像素值。

$$
g (i, j) = \sum_ {m, n} w (m, n) f (i - m, j - n)
$$

- $f$ : 原始图像；
- $g$ : 滤波后的图像；- $w$ ：滤波模板或卷积核；
- 邻域大小决定考虑多少周围信息。

一句话

滤波的核心，是用局部邻域中的信息重新估计当前像素。

## 均值滤波：最简单的平滑方法

基本思想

用邻域内像素的平均值替代当前像素值。

$$
g (i, j) = \frac {1}{| \Omega |} \sum_ {(m, n) \in \Omega} f (i + m, j + n)
$$

优点

实现简单
- 可以减弱随机噪声
- 计算速度快

缺点

- 会模糊边缘
- 细节容易被抹平
- 对椒盐噪声效果一般

## 高斯滤波：更自然的平滑

基本思想

距离中心越近的像素权重越大，距离越远的像素权重越小。

$$
G (x, y) = \frac {1}{2 \pi \sigma^ {2}} \exp \left(- \frac {x ^ {2} + y ^ {2}}{2 \sigma^ {2}}\right)
$$

- $\sigma$ 控制平滑程度；
- $\sigma$ 越大，图像越平滑；
- 高斯滤波比均值滤波更加自然；
- 常用于去噪和边缘检测前的预处理。

直观理解

高斯滤波相当于 “中心像素附近的信息更可信，远处信息影响较小”。

## 中信滤波：对椒盐哑吉特别有效基本思想

用邻域中所有像素的中位数替代当前像素。

$$
g (i, j) = \mathrm{median} \{f (i + m, j + n): (m, n) \in \Omega \}
$$

适用场景

- 图像中出现黑白随机点；
- 传输或传感器带来脉冲噪声；
- 希望去噪同时尽量保留边缘。

关键区别

均值滤波容易被极端噪声值影响，而中值滤波对极端值更稳健。

## 第二部分阶段小结

1 图像增强的目标是让图像更清楚、更有用。
② 点运算只改变单个像素的灰度值。
③ 灰度变换可以调节亮度和对比度。
4 直方图可以描述图像的灰度分布。
⑤ 直方图均衡化可以增强对比度。
⑥ 滤波通过邻域信息改善图像质量。
⑦ 均值滤波、高斯滤波、中值滤波适合不同噪声场景。

下一步

平滑滤波可以去噪，但也可能模糊边缘。那么，如何突出边缘和细节？

接下来：锐化与边缘检测

---

## 演示代码 — YCrCb 亮度通道直方图均衡化

```python
import cv2
import matplotlib.pyplot as plt
import numpy as np

# 读取图片 (OpenCV 默认 BGR 顺序)
img_bgr = cv2.imread('../images/lena_color_512.png')
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# 转换到 YCrCb 颜色空间
img_ycrbc = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)

# 仅对 Y (亮度) 通道进行直方图均衡化，保持 Cr, Cb 不变
img_ycrbc[:, :, 0] = cv2.equalizeHist(img_ycrbc[:, :, 0])

# 转换回 RGB 空间
img_eq = cv2.cvtColor(img_ycrbc, cv2.COLOR_YCrCb2RGB)

# 2x2 画布：原图 vs 均衡化 + 各自的直方图
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

images = [img_rgb, img_eq]
titles = ["Original", "Equalized (Y channel)"]

for col in range(2):
    axes[0, col].imshow(images[col])
    axes[0, col].set_title(titles[col], fontsize=13)
    axes[0, col].axis('off')

    gray = cv2.cvtColor(images[col], cv2.COLOR_RGB2GRAY)
    axes[1, col].hist(gray.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.8)
    axes[1, col].set_title(f'{titles[col]} - Histogram', fontsize=13)
    axes[1, col].set_xlim([0, 256])
    axes[1, col].set_xlabel('Pixel Intensity')
    axes[1, col].set_ylabel('Frequency')

plt.tight_layout()
plt.show()
```

<a href="https://mybinder.org/v2/gh/ln2a/IMAGE_ENGINEERING_ECNU/main?urlpath=%2Fdoc%2Ftree%2Fpython-tutorial%2Fex2.ipynb" target="_blank" style="display: inline-block; background-color: #03a9f4; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-size: 15px; margin-top: 8px;">运行此代码 →</a>
