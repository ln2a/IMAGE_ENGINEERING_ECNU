"""Build the self-contained Chapter 5 notebooks and preview figures.

Run this file after installing requirements.txt:

    python python-tutorial/build_ch05_examples.py

The generated experiments use deterministic synthetic images, so they do not
depend on a network download and produce the same teaching result every time.
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "python-tutorial"
DOC_IMAGE_DIR = ROOT / "docs" / "images"


def markdown(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": dedent(text).strip().splitlines(keepends=True),
    }


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(text).strip().splitlines(keepends=True),
    }


def notebook(cells: list[dict]) -> dict:
    for index, cell in enumerate(cells):
        cell["id"] = f"ch05-cell-{index:02d}"
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


COMMON_CODE = r"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SEED = 2026
rng = np.random.default_rng(SEED)
CLASS_NAMES = np.array(["circle", "square", "triangle"])
CLASS_COLORS = np.array([
    [0.90, 0.20, 0.20],
    [0.15, 0.65, 0.25],
    [0.15, 0.35, 0.90],
])

def polygon_mask(height, width, vertices):
    '''Vectorized ray-casting test: pixels inside an arbitrary polygon.'''
    yy, xx = np.mgrid[:height, :width]
    x = xx + 0.5
    y = yy + 0.5
    inside = np.zeros((height, width), dtype=bool)
    vertices = np.asarray(vertices, dtype=float)
    j = len(vertices) - 1
    for i in range(len(vertices)):
        xi, yi = vertices[i]
        xj, yj = vertices[j]
        crosses = ((yi > y) != (yj > y))
        x_cross = (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
        inside ^= crosses & (x < x_cross)
        j = i
    return inside

def shape_mask(kind, size=64, center=None, scale=0.52, angle=0.0):
    '''Create a circle, square or triangle mask.'''
    cy, cx = center if center is not None else (size / 2, size / 2)
    yy, xx = np.mgrid[:size, :size]
    radius = size * scale / 2
    if kind == 0:
        return (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2

    count = 4 if kind == 1 else 3
    base = angle + (-np.pi / 4 if kind == 1 else -np.pi / 2)
    angles = base + np.arange(count) * 2 * np.pi / count
    vertices = np.column_stack([
        cx + radius * np.cos(angles),
        cy + radius * np.sin(angles),
    ])
    return polygon_mask(size, size, vertices)

def render_shape(kind, size=64, center=None, scale=0.52, angle=0.0,
                 color=None, noise=0.015, rng=rng):
    mask = shape_mask(kind, size, center, scale, angle)
    image = np.full((size, size, 3), 0.96, dtype=float)
    if color is None:
        color = CLASS_COLORS[kind]
    image[mask] = color
    image += rng.normal(0, noise, image.shape)
    return np.clip(image, 0, 1), mask

def foreground_mask(image):
    '''Separate colorful/dark objects from the nearly white background.'''
    return np.linalg.norm(image - 0.96, axis=2) > 0.20

def binary_perimeter(mask):
    padded = np.pad(mask, 1, constant_values=False)
    eroded = (
        padded[1:-1, 1:-1]
        & padded[:-2, 1:-1]
        & padded[2:, 1:-1]
        & padded[1:-1, :-2]
        & padded[1:-1, 2:]
    )
    return mask & ~eroded

def extract_features(image):
    '''Area ratio, circularity, extent and radial-distance variation.'''
    mask = foreground_mask(image)
    ys, xs = np.where(mask)
    area = float(mask.sum())
    perimeter = float(binary_perimeter(mask).sum())
    height = ys.max() - ys.min() + 1
    width = xs.max() - xs.min() + 1
    extent = area / (height * width)
    circularity = 4 * np.pi * area / max(perimeter ** 2, 1)
    cy, cx = ys.mean(), xs.mean()
    by, bx = np.where(binary_perimeter(mask))
    radii = np.sqrt((by - cy) ** 2 + (bx - cx) ** 2)
    radial_cv = radii.std() / max(radii.mean(), 1e-6)
    area_ratio = area / mask.size
    return np.array([area_ratio, circularity, extent, radial_cv])

def make_classification_dataset(
    samples_per_class=80, scale_range=(0.43, 0.62), rng=rng
):
    images, labels, features = [], [], []
    for label in range(3):
        for _ in range(samples_per_class):
            scale = rng.uniform(*scale_range)
            offset = rng.integers(-5, 6, size=2)
            angle = rng.uniform(-0.25, 0.25)
            color = rng.uniform(0.12, 0.88, size=3)
            if color.mean() > 0.72:
                color *= 0.65
            image, _ = render_shape(
                label,
                center=(32 + offset[0], 32 + offset[1]),
                scale=scale,
                angle=angle,
                color=color,
                rng=rng,
            )
            images.append(image)
            labels.append(label)
            features.append(extract_features(image))
    return np.asarray(images), np.asarray(labels), np.asarray(features)

class NearestCentroidClassifier:
    '''A tiny, interpretable classifier with one prototype per class.'''
    def fit(self, X, y):
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + 1e-8
        Z = (X - self.mean_) / self.scale_
        self.classes_ = np.unique(y)
        self.centroids_ = np.vstack([Z[y == c].mean(axis=0) for c in self.classes_])
        return self

    def predict(self, X):
        Z = (X - self.mean_) / self.scale_
        distances = ((Z[:, None, :] - self.centroids_[None, :, :]) ** 2).sum(axis=2)
        return self.classes_[distances.argmin(axis=1)]
"""


CLASSIFICATION_CELLS = [
    markdown(
        """
        # 第五章实验 1：可视化特征与图像分类

        本实验完全离线运行。程序自动生成带有随机位置、尺度、旋转、颜色和轻微噪声的
        **圆形、正方形、三角形**图像，然后：

        1. 可视化颜色直方图和形状边界；
        2. 提取面积比、圆形度、外接矩形填充率和径向变化四个特征；
        3. 使用最近质心分类器完成三分类；
        4. 显示混淆矩阵和测试图像预测结果。

        固定随机种子后，每次运行都可复现，不需要下载数据或模型。
        """
    ),
    code(COMMON_CODE),
    markdown("## 1. 颜色与形状特征可视化"),
    code(
        """
        demo, demo_mask = render_shape(
            kind=2, center=(30, 35), scale=0.58, angle=0.12,
            color=np.array([0.20, 0.45, 0.85])
        )
        edge = binary_perimeter(demo_mask)

        fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
        axes[0].imshow(demo)
        axes[0].set_title("Input image")
        axes[1].imshow(demo)
        ey, ex = np.where(edge)
        axes[1].scatter(ex, ey, s=5, c="yellow")
        axes[1].set_title("Extracted boundary")
        for channel, color, name in zip(range(3), "rgb", ["R", "G", "B"]):
            axes[2].hist(demo[..., channel].ravel(), bins=32, alpha=0.55,
                         color=color, label=name)
        axes[2].set_title("RGB color histogram")
        axes[2].set_xlabel("Pixel value")
        axes[2].legend()
        axes[0].axis("off")
        axes[1].axis("off")
        plt.tight_layout()
        plt.show()

        names = ["面积比", "圆形度", "填充率", "径向变化"]
        print(dict(zip(names, np.round(extract_features(demo), 3))))
        """
    ),
    markdown("## 2. 自动生成数据集"),
    code(
        """
        images, labels, features = make_classification_dataset(samples_per_class=80)

        fig, axes = plt.subplots(3, 6, figsize=(11, 5.8))
        for row, label in enumerate(range(3)):
            indices = np.where(labels == label)[0][:6]
            for ax, idx in zip(axes[row], indices):
                ax.imshow(images[idx])
                ax.axis("off")
            axes[row, 0].set_ylabel(CLASS_NAMES[label], fontsize=12)
        plt.suptitle("Synthetic training data")
        plt.tight_layout()
        plt.show()

        print("数据形状:", images.shape)
        print("每类样本数:", np.bincount(labels))
        """
    ),
    markdown("## 3. 训练简单模型并评价"),
    code(
        """
        order = rng.permutation(len(labels))
        split = int(len(order) * 0.75)
        train_idx, test_idx = order[:split], order[split:]

        model = NearestCentroidClassifier().fit(features[train_idx], labels[train_idx])
        pred = model.predict(features[test_idx])
        accuracy = (pred == labels[test_idx]).mean()

        confusion = np.zeros((3, 3), dtype=int)
        for truth, guess in zip(labels[test_idx], pred):
            confusion[truth, guess] += 1

        fig, ax = plt.subplots(figsize=(5, 4))
        im = ax.imshow(confusion, cmap="Blues")
        for i in range(3):
            for j in range(3):
                ax.text(j, i, confusion[i, j], ha="center", va="center",
                        color="white" if confusion[i, j] > confusion.max() / 2 else "black")
        ax.set_xticks(range(3), CLASS_NAMES)
        ax.set_yticks(range(3), CLASS_NAMES)
        ax.set_xlabel("Predicted class")
        ax.set_ylabel("True class")
        ax.set_title(f"Confusion matrix (accuracy {accuracy:.1%})")
        fig.colorbar(im, ax=ax, fraction=0.046)
        plt.tight_layout()
        plt.show()

        print(f"测试集准确率: {accuracy:.2%}")
        """
    ),
    markdown("## 4. 可视化预测结果"),
    code(
        """
        show_idx = test_idx[:12]
        show_pred = model.predict(features[show_idx])
        fig, axes = plt.subplots(3, 4, figsize=(9, 7))
        for ax, idx, guess in zip(axes.ravel(), show_idx, show_pred):
            truth = labels[idx]
            ax.imshow(images[idx])
            ax.set_title(
                f"Pred: {CLASS_NAMES[guess]}\\nTrue: {CLASS_NAMES[truth]}",
                color="green" if guess == truth else "red",
            )
            ax.axis("off")
        plt.tight_layout()
        plt.show()
        """
    ),
    markdown(
        """
        ## 结论

        这个小实验刻意使用简单模型：当类别可由清晰的形状特征区分时，最近质心分类器
        已经足够有效。它也揭示了传统识别流程：

        **图像 → 分割前景 → 提取特征 → 分类器 → 类别。**
        """
    ),
]


DETECTION_CODE = r"""
def connected_components(mask, min_area=40):
    '''Return bounding boxes (x1, y1, x2, y2) for 4-connected regions.'''
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    boxes = []
    for y0, x0 in zip(*np.where(mask & ~visited)):
        if visited[y0, x0]:
            continue
        stack = [(y0, x0)]
        visited[y0, x0] = True
        xs, ys = [], []
        while stack:
            y, x = stack.pop()
            xs.append(x)
            ys.append(y)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < height and 0 <= nx < width:
                    if mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))
        if len(xs) >= min_area:
            boxes.append((min(xs), min(ys), max(xs) + 1, max(ys) + 1))
    return boxes

def make_detection_scene(size=192, rng=rng):
    image = np.full((size, size, 3), 0.96, dtype=float)
    truth = []
    # Fixed separated cells make the demonstration deterministic and avoid overlap.
    cells = [(48, 48), (48, 144), (144, 48), (144, 144)]
    labels = rng.choice(3, size=4, replace=True)
    for (cy, cx), label in zip(cells, labels):
        cy += int(rng.integers(-10, 11))
        cx += int(rng.integers(-10, 11))
        scale = rng.uniform(0.28, 0.38)
        angle = rng.uniform(-0.22, 0.22)
        color = rng.uniform(0.10, 0.82, size=3)
        if color.mean() > 0.68:
            color *= 0.60
        mask = shape_mask(label, size, center=(cy, cx), scale=scale, angle=angle)
        image[mask] = color
        ys, xs = np.where(mask)
        truth.append({
            "label": int(label),
            "box": (int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)),
        })
    image += rng.normal(0, 0.012, image.shape)
    return np.clip(image, 0, 1), truth

def crop_to_square(image, box, output_size=64):
    x1, y1, x2, y2 = box
    crop = image[y1:y2, x1:x2]
    canvas = np.full((output_size, output_size, 3), 0.96, dtype=float)
    height, width = crop.shape[:2]
    scale = min((output_size - 10) / height, (output_size - 10) / width)
    new_h = max(1, int(round(height * scale)))
    new_w = max(1, int(round(width * scale)))
    yi = np.minimum((np.arange(new_h) / scale).astype(int), height - 1)
    xi = np.minimum((np.arange(new_w) / scale).astype(int), width - 1)
    resized = crop[yi[:, None], xi[None, :]]
    top = (output_size - new_h) // 2
    left = (output_size - new_w) // 2
    canvas[top:top + new_h, left:left + new_w] = resized
    return canvas

def detect_objects(image, classifier):
    mask = foreground_mask(image)
    boxes = connected_components(mask, min_area=120)
    detections = []
    for box in boxes:
        crop = crop_to_square(image, box)
        feature = extract_features(crop)
        label = int(classifier.predict(feature[None, :])[0])
        detections.append({"label": label, "box": box})
    return mask, detections

def box_iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    intersection = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - intersection
    return intersection / max(union, 1)

def draw_detections(ax, image, detections, title):
    ax.imshow(image)
    for item in detections:
        x1, y1, x2, y2 = item["box"]
        color = CLASS_COLORS[item["label"]]
        ax.add_patch(Rectangle(
            (x1, y1), x2 - x1, y2 - y1,
            fill=False, edgecolor=color, linewidth=2.5
        ))
        ax.text(
            x1, max(2, y1 - 3), CLASS_NAMES[item["label"]],
            color="white", fontsize=10,
            bbox={"facecolor": color, "alpha": 0.9, "pad": 2, "edgecolor": "none"},
        )
    ax.set_title(title)
    ax.axis("off")
"""


DETECTION_CELLS = [
    markdown(
        """
        # 第五章实验 2：多目标检测、画框与分割

        本实验生成一张含多个随机几何目标的场景图，并执行完整检测流程：

        **前景分割 → 连通域定位 → 边界框 → 形状特征分类 → 画框与类别标签。**

        定位由像素级前景掩膜得到，因此在该数据集上预测框与真实框可以高度重合。
        分类器沿用实验 1 的最近质心模型。整个 Notebook 无需联网和预训练权重。
        """
    ),
    code(COMMON_CODE),
    markdown("## 1. 训练轻量形状分类器"),
    code(
        """
        train_images, train_labels, train_features = make_classification_dataset(
            samples_per_class=90, scale_range=(0.76, 0.88)
        )
        classifier = NearestCentroidClassifier().fit(train_features, train_labels)
        train_accuracy = (
            classifier.predict(train_features) == train_labels
        ).mean()
        print(f"训练数据准确率: {train_accuracy:.2%}")
        """
    ),
    code(DETECTION_CODE),
    markdown("## 2. 生成场景并检测所有目标"),
    code(
        """
        scene, truth = make_detection_scene()
        foreground, detections = detect_objects(scene, classifier)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(scene)
        axes[0].set_title("Input scene")
        axes[0].axis("off")
        axes[1].imshow(foreground, cmap="gray")
        axes[1].set_title("Foreground mask")
        axes[1].axis("off")
        draw_detections(
            axes[2], scene, detections,
            f"Detections: {len(detections)} objects"
        )
        plt.tight_layout()
        plt.show()
        """
    ),
    markdown("## 3. 用 IoU 和类别准确率评价检测结果"),
    code(
        """
        matched_ious = []
        matched_correct = []
        for target in truth:
            best = max(detections, key=lambda det: box_iou(target["box"], det["box"]))
            matched_ious.append(box_iou(target["box"], best["box"]))
            matched_correct.append(target["label"] == best["label"])

        print("每个目标的 IoU:", np.round(matched_ious, 3))
        print(f"平均 IoU: {np.mean(matched_ious):.3f}")
        print(f"类别准确率: {np.mean(matched_correct):.2%}")
        print(f"真实目标数 / 检出目标数: {len(truth)} / {len(detections)}")
        """
    ),
    markdown("## 4. 批量测试不同场景"),
    code(
        """
        fig, axes = plt.subplots(2, 3, figsize=(13, 8))
        all_ious, all_correct = [], []
        for ax in axes.ravel():
            test_scene, test_truth = make_detection_scene()
            _, test_det = detect_objects(test_scene, classifier)
            draw_detections(ax, test_scene, test_det, f"{len(test_det)} objects")
            for target in test_truth:
                best = max(test_det, key=lambda det: box_iou(target["box"], det["box"]))
                all_ious.append(box_iou(target["box"], best["box"]))
                all_correct.append(target["label"] == best["label"])
        plt.tight_layout()
        plt.show()

        print(f"批量测试平均 IoU: {np.mean(all_ious):.3f}")
        print(f"批量测试类别准确率: {np.mean(all_correct):.2%}")
        """
    ),
    markdown(
        """
        ## 适用范围与局限

        该检测器在背景干净、目标互不粘连的教学数据上速度快、定位准、容易理解。
        如果背景复杂、目标互相遮挡，通常需要更强的检测模型，例如 YOLO 或 Faster R-CNN。
        教学中先掌握“分割—连通域—分类—画框”的完整链路，再理解深度检测器会更自然。
        """
    ),
]


def save_notebook(name: str, cells: list[dict]) -> None:
    path = NOTEBOOK_DIR / name
    path.write_text(
        json.dumps(notebook(cells), ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )


def preview_assets() -> None:
    """Render lightweight static previews used by the MkDocs chapter."""
    namespace: dict = {}
    exec(COMMON_CODE, namespace)
    exec(DETECTION_CODE, namespace)

    local_rng = np.random.default_rng(2026)
    images, labels, features = namespace["make_classification_dataset"](
        samples_per_class=80, rng=local_rng
    )
    order = local_rng.permutation(len(labels))
    split = int(len(order) * 0.75)
    train_idx, test_idx = order[:split], order[split:]
    model = namespace["NearestCentroidClassifier"]().fit(
        features[train_idx], labels[train_idx]
    )
    pred = model.predict(features[test_idx])

    fig, axes = plt.subplots(2, 4, figsize=(10, 5))
    for ax, idx, guess in zip(axes.ravel(), test_idx[:8], pred[:8]):
        ax.imshow(images[idx])
        ax.set_title(
            f"Pred: {namespace['CLASS_NAMES'][guess]}\n"
            f"True: {namespace['CLASS_NAMES'][labels[idx]]}"
        )
        ax.axis("off")
    fig.suptitle(f"Shape classification accuracy: {(pred == labels[test_idx]).mean():.1%}")
    fig.tight_layout()
    fig.savefig(DOC_IMAGE_DIR / "ch05-classification-preview.png", dpi=150)
    plt.close(fig)

    _, detector_labels, detector_features = namespace["make_classification_dataset"](
        samples_per_class=90, scale_range=(0.76, 0.88), rng=local_rng
    )
    detector_model = namespace["NearestCentroidClassifier"]().fit(
        detector_features, detector_labels
    )
    scene, truth = namespace["make_detection_scene"](rng=local_rng)
    foreground, detections = namespace["detect_objects"](scene, detector_model)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(foreground, cmap="gray")
    axes[0].set_title("Foreground segmentation")
    axes[0].axis("off")
    namespace["draw_detections"](axes[1], scene, detections, "Object detection and boxes")
    fig.tight_layout()
    fig.savefig(DOC_IMAGE_DIR / "ch05-detection-preview.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    DOC_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    save_notebook("ex11_ch05.ipynb", CLASSIFICATION_CELLS)
    save_notebook("ex12_ch05.ipynb", DETECTION_CELLS)
    preview_assets()
    print("Chapter 5 notebooks and preview images generated.")
