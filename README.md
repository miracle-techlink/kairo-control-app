# Kairo Control App

Project Kairo 的机器人控制台: 面向 ReBotArm 做硬件配置、遥操作、数据采集、训练任务提交和真机推理入口。

这个仓库基于 MakerMods-App 的 FastAPI + Next.js wizard 结构改造，默认 single-arm profile 接入 `rebot_datacollect` 中的 reBot B601-RS + StarAI Violin + Orbbec 深度相机链路。

## 仓库内容

```text
backend/                         FastAPI 后端，封装硬件扫描、遥操作、采集、训练、推理 API
frontend/                        Next.js 前端，Kairo Control wizard
hardware/rebotarm/rebot_datacollect/
                                 ReBotArm 的 LeRobot 插件、teleop/record/profile 脚本
requirements.txt                 后端依赖，需安装到同一个 LeRobot Python 环境
```

## ReBotArm 默认硬件

- 从臂: Seeed reBot B601-RS，RobStride 7 轴，SocketCAN，默认 `CAN=can0`
- 主臂: StarAI Violin，UART 舵机，默认 `LEADER_PORT=/dev/ttyCH341USB0`
- 腕部相机: Orbbec Gemini 305，默认 `WRIST_CAM=CV275610002L`
- 第二视角: UVC USB 相机，UI 中配置为 front camera，默认可用 `FRONT_CAM=/dev/video10`
- 主机: Jetson Thor / reComputer J601 优先

## 启动

后端必须运行在装好 LeRobot、reBot 插件和相机依赖的同一个 Python 环境里。

```bash
cd kairo-control-app

# Python backend
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Web frontend
cd frontend
npm install
npm run dev:linux -- --hostname 0.0.0.0 --port 3000
```

打开:

```text
http://localhost:3000
```

## ReBotArm Profile

默认启用:

```bash
export KAIRO_ROBOT_PROFILE=rebotarm
```

single-arm 模式下 UI 字段含义:

- follower port: ReBot CAN 口，例如 `can0` / `can5`
- leader port: StarAI 主臂串口，例如 `/dev/ttyCH341USB0`
- first camera: front camera，例如 `/dev/video10`

后端会调用:

```bash
hardware/rebotarm/rebot_datacollect/scripts/teleop_rebot.sh
hardware/rebotarm/rebot_datacollect/scripts/record_rebot.sh
```

常用覆盖变量:

```bash
export LEROBOT_PYTHON=/path/to/lerobot/env/bin/python
export CAN=can0
export LEADER_PORT=/dev/ttyCH341USB0
export WRIST_CAM=CV275610002L
export NONBLOCK=1
export DEPTH_PRESET=ultrafast
```

## 采集链路

1. 在机器上先拉起 CAN:

```bash
sudo bash hardware/rebotarm/rebot_datacollect/scripts/setup_rebot_can.sh
```

2. 前端选择 `ReBotArm Single`。
3. Ports 里设置 CAN 和主臂串口。
4. Cameras 里设置 front camera；腕部 Orbbec 通过 `WRIST_CAM` 环境变量指定。
5. Teleop 先空跑确认主从映射、夹爪方向、相机画面。
6. Record 填 HuggingFace repo、任务描述、episode 数量和时长，启动 LeRobot 数据采集。

## 训练和推理

当前训练页保留云端训练任务提交入口；推理页保留 LeRobot policy path 真机执行入口。后续会把 Project Kairo 的 TTT / VLA 训练脚本、RoboDojo/RoboTwin/VLA-Perf benchmark 入口进一步接进这个 app。

## 来源

本仓库的 UI/后端骨架来自 `makermods-robotics/MakerMods-App`，ReBotArm 硬件脚本来自 `miracle-techlink/rebot_datacollect`。当前仓库作为 Project Kairo 内部控制台继续维护。
