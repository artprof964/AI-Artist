# Hardware Requirements - Latest

The selected implementation uses OpenClaw plus a hosted OpenAI LLM, so local
LLM inference hardware is no longer required for the MVP. GPU capacity is still
needed for ComfyUI image generation unless that workload is moved to a GPU
cloud provider.

## Minimum

```text
CPU:      8 cores
RAM:      32 GB
GPU:      optional for MVP if ComfyUI runs in cloud; 16 GB VRAM if local
Storage:  1 TB NVMe
```

## Smooth Workstation

```text
CPU:      16-24 cores
RAM:      64-128 GB
GPU:      24-48 GB VRAM for local ComfyUI
Storage:  2 TB OS NVMe + 4 TB data NVMe
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
Hosted OpenAI -> LLM reasoning
GPU 1 -> ComfyUI media generation
CPU workers -> parsing / ingestion / source processing
NVMe -> Qdrant + PostgreSQL + MinIO hot data
```

## Validation

```text
MVP hardware validation checks:
- hosted OpenAI smoke test works without local LLM GPU inference
- Docker Compose services pass health checks
- ComfyUI path is either mocked, local-GPU backed, or cloud-GPU backed
- image-generation tasks fail cleanly when no approved GPU path exists
```
