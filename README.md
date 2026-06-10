# 26-27ML-Final

本仓库是课程作业的复现实验与图证材料包，主题为：

**密钥感知的空天地海一体化量子电磁系统深度强化学习优化设计**

仓库重点保留可复现代码、HFSS 工程文件、MATLAB/Python 数值仿真图证和关键数据表。

## 仓库内容

- `data/figures/`  
  系统级 DRL、QKD、RIS、统计置信区间和架构闭环图证。

- `data/hfss/periodic_unit/`  
  标准 RIS 周期反射单元 HFSS 工程、HFSS 导出的模型视图、反射相位/幅度表和 2-bit 相位码本。

- `data/hfss/finite_array/`  
  16x16 与 8x8 RIS 有限阵列 HFSS 工程、HFSS 导出的阵列模型视图和求解记录。

- `src/python/`  
  RIS 相位码本、HFSS 到系统模型接口图、统计置信区间图等 Python 复现脚本。

- `src/matlab/`  
  QKD 天气/密钥池、RIS 阵列波束和系统级数值仿真脚本。

- `src/hfss/`  
  AEDT/HFSS 自动化建模脚本，包括周期单元和有限阵列模型。

## 技术路线

报告主线对应如下闭环：

`P0 优化目标 -> CMDP 建模 -> KA-GNN-PPO 策略学习 -> 安全投影 -> QKD/RIS/HFSS/MATLAB 图证 -> 系统指标反馈`

其中 RIS 证据分为两层：

- **HFSS 层**：标准周期单元、Floquet Port、Lattice Pair 周期边界，以及有限阵列工程模型。
- **MATLAB/Python 层**：相位码本、远场波束、鲁棒性、置信区间和系统级 `H_eff`、`SINR`、`R_i[n]`、`D_i[n]` 映射。

## 仿真边界

本仓库面向课程级复现实验。16x16 RIS 有限阵列 HFSS 工程已经提供，但完整全波求解对内存要求较高；8x8 有限阵列作为本机可运行的工程级验证补充。系统级性能对比、QKD/RIS 闭环和统计图由 MATLAB/Python 脚本生成。

复现步骤见 `REPRODUCE.md`。
