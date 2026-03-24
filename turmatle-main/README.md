# Turmatle 项目说明
## 1. 项目简介
本项目围绕**几何图形参数化生成、结构化识别与增强绘制**展开，构建了一个较完整的技术闭环，主要包括以下几个部分：

项目主要分为两个部分：
- `turmatle-main`：几何图元类、数据生成、模型训练、测试分析与手绘图形探索
- `turmatle_pro`：识别结果可视化与增强绘制系统
---
## 2. 项目整体结构
### 2.1 `turmatle-main`
`turmatle-main` 是本项目的主体，负责数据生成、模型训练、模型测试和实验分析。
主要目录说明如下：
- `geom`：基础几何图元类与绘图逻辑
- `create_data`：预训练数据生成脚本
- `datas`：预训练数据保存目录[见huggingface]
- `create_fine_data`：微调数据生成脚本
- `datas_finetuning`：微调数据保存目录[见huggingface]
- `create_val_data`：测试数据生成脚本
- `val_datas`：测试数据保存目录[见huggingface]
- `P2T-Trainer`：模型训练与预测代码[见huggingface]
- `val_model_result`：预训练模型测试结果分析
- `val_finetune_model_result`：微调模型测试结果分析
- `visualization_compare`：预训练模型与微调模型结果对比代码
- `visualize_results.py`：绘制综合对比图
- `draw_explore`：手绘图形预处理、推理与重绘实验
- `inference.txt`：推理相关命令记录
- `new_models`：预训练模型[见huggingface：https://huggingface.co/zi-hui/Turmatle_pretrain_model/tree/main]
- `new_models_finetuning`微调后的模型[见huggingface:https://huggingface.co/zi-hui/Turmatle_finetune_model/tree/main]

### 2.2 `turmatle_pro`
`turmatle_pro` 是识别结果可视化与增强绘制系统，主要用于将识别得到的结构化几何描述重新组织为可演示、可标注、可高亮的绘图过程。
主要目录说明如下：
- `turmatle_pro/geom`：增强版几何图元类
- `turmatle_pro/examples`：增强绘制与结果可视化示例代码
---

## 3. 环境与依赖说明
本项目主要基于 Python 实现，涉及以下核心依赖：
- `Python`
- `turtle`
- `Pillow`
- `OpenCV`
- `NumPy`
- `PyTorch`
- `Transformers`
- `albumentations`
- `matplotlib`

## 4. 预训练数据生成流程
预训练数据由 `create_data` 目录中的脚本生成，输出保存到 `datas` 目录中。
流程如下：
1. 运行 `turmatle-main/create_data` 中的各个生成脚本，生成基础几何图形数据
2. 生成后的图像与标签保存在 `turmatle-main/datas` 下
3. 运行 `turmatle-main/P2T-Trainer/scripts/split_labels.py`，将标签划分为训练集与验证集
4. 划分结果保存在 `turmatle-main/datas/trocr-train-index` 中，生成 `train.tsv` 和 `dev.tsv`
5. 运行 `turmatle-main/fix_paths.py`，将路径中的反斜杠替换为正斜杠
6. 在 `turmatle-main/P2T-Trainer` 中使用 `gpu.Makefile` 里的 `train-trocr` 任务进行预训练
### 相关目录
- 数据生成脚本：`turmatle-main/create_data`
- 生成数据目录：`turmatle-main/datas`
- 数据划分脚本：`turmatle-main/P2T-Trainer/scripts/split_labels.py`
- 数据索引目录：`turmatle-main/datas/trocr-train-index`
---

## 5. 微调数据生成流程
微调数据由 `create_fine_data` 中的脚本生成，输出保存到 `datas_finetuning` 目录中。
流程如下：
1. 运行 `turmatle-main/create_fine_data` 中的各个脚本，生成微调数据
2. 生成后的图像与标签保存在 `turmatle-main/datas_finetuning` 中
3. 运行 `turmatle-main/P2T-Trainer/scripts/split_labels_finetuning.py`，将标签划分为训练集与验证集
4. 划分结果保存在 `turmatle-main/datas_finetuning/finetuning-trocr-index` 中,生成 `train.tsv` 和 `dev.tsv`
5. 运行 `turmatle-main/fix_paths.py`，将路径中的反斜杠替换为正斜杠
6. 在 `turmatle-main/P2T-Trainer` 中使用 `gpu.Makefile` 里的 `finetune-trocr` 任务进行微调训练
### 相关目录
- 数据生成脚本：`turmatle-main/create_fine_data`
- 生成数据目录：`turmatle-main/datas_finetuning`
- 数据划分脚本：`turmatle-main/P2T-Trainer/scripts/split_labels_finetuning.py`
- 数据索引目录：`turmatle-main/datas_finetuning/finetuning-trocr-index`
---

## 6. 测试数据生成流程
测试数据由 `create_val_data` 中的脚本生成，输出保存到 `val_datas` 中。
流程如下：
1. 运行 `turmatle-main/create_val_data` 中的脚本生成测试数据
2. 图像与标签保存到 `turmatle-main/val_datas`
3. 运行 `turmatle-main/fix_val_paths.py`，统一路径格式
### 相关目录
- 数据生成脚本：`turmatle-main/create_val_data`
- 测试数据目录：`turmatle-main/val_datas`
---

## 7. 模型训练部分说明
模型训练代码位于：
- `turmatle-main/P2T-Trainer`
该目录包含以下内容：
- `models`：训练好的模型或模型相关目录
- `p2t`：数据增强、数据集读取、训练与推理核心代码
- `scripts`：训练/微调数据划分脚本
- `wandb`：训练过程日志
- `gpu.Makefile`：训练与微调命令入口
- `._trocr-small2040-handwritten-initial-model-2025`：基础模型文件
训练后的模型通常保存在 `checkpoints` 目录中。
---

## 8. 推理说明
推理相关命令记录在：
- `turmatle-main/inference.txt`
  
推理前需安装
- pip install pix2text
该文件中包含模型推理的命令示例，可用于对单张图片或测试数据进行识别。
---

## 9. 手绘图形探索与处理
手绘图形相关实验位于：
- `turmatle-main/draw_explore`
该目录主要用于手绘几何图形的预处理、推理和重绘。
### 主要文件说明
- `images`：保存原始手绘图形与预处理后的图像
- `preprocess_handdrawn_copy.py`：手绘图像预处理脚本
- `draw_original.py`：将推理得到的结构化代码重新绘制为几何图形
- `predict`：保存重绘结果或预测可视化结果
### 手绘处理流程
1. 将手绘图像放入 `draw_explore/images`
2. 运行 `preprocess_handdrawn_copy.py` 对手绘图像进行预处理
3. 使用模型对处理后的图像进行推理
4. 将推理得到的结构化描述交给 `draw_original.py` 或相关脚本进行重绘
5. 输出结果保存到 `predict` 目录
---

## 10. 预训练模型测试结果分析
预训练模型相关分析代码位于：
- `turmatle-main/val_model_result`
### 主要文件说明
- `batch_predict_pretrain.py`  
  批量使用预训练模型预测 `val_datas/images/` 中的图片  
  输出标签文件：`predict_pretrain_labels copy 2.txt`
- `calculate_accuracy.py`  
  计算预训练模型测试结果准确率  
  输出文件：`accuracy_copy_result 22.txt`
- `category_stats.py`  
  按类别统计预训练模型测试结果  
  输出：
  - `category_stats_result.txt`
  - `category_charts/`
- `draw_predictions.py`  
  可视化预训练模型预测结果  
  输出文件：`predictions_pretrain.png`
---

## 11. 微调模型测试结果分析
微调模型相关分析代码位于：
- `turmatle-main/val_finetune_model_result`
### 主要文件说明
- `batch_predict_finetune.py`  
  批量使用微调模型预测 `val_datas/images/` 中的图片  
  输出标签文件：`predict_finetune_labels copy 2.txt`
- `calculate_accuracy.py`  
  计算微调模型测试结果准确率  
  输出文件：`accuracy_finetune_copy_result 22.txt`
- `category_stats.py`  
  按类别统计微调模型测试结果  
  输出：
  - `category_stats_result.txt`
  - `category_charts/`
- `draw_predictions_finetune.py`  
  可视化微调模型预测结果  
  输出文件：`predictions_finetune.png`
---

## 12. 预训练与微调结果对比
对比分析相关代码位于：
- `turmatle-main/visualization_compare`
此外：
- `turmatle-main/visualize_results.py`  
  用于绘制综合对比图，输出到 `visualization_results_2` 目录中
该部分主要用于对比预训练模型与微调模型在整体准确率、类别分布和可视化结果上的差异。
---
