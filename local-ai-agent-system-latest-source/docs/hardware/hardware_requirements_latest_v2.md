# Hardware Requirements - Latest

## Minimum

```text
CPU:      12 cores
RAM:      64 GB
GPU:      16 GB VRAM
Storage:  2 TB NVMe
```

## Smooth Workstation

```text
CPU:      24 cores
RAM:      128 GB
GPU:      24-48 GB VRAM
Storage:  2 TB OS NVMe + 4-8 TB data NVMe
Network:  2.5/10 GbE
```

## Better Single Server

```text
CPU:      32-64 cores
RAM:      256 GB
GPU:      2x 24 GB or 1-2x 48 GB VRAM
Storage:  8-16 TB NVMe data
Network:  10 GbE
```

## Best Layout

```text
GPU 1 -> vLLM local LLM
GPU 2 -> ComfyUI media generation
CPU workers -> parsing / ingestion / embeddings
NVMe -> Qdrant + PostgreSQL + MinIO hot data
```
