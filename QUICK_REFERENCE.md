# Quick Reference: Node Migration Map

## Node Type Mappings

### Detection Nodes

| GroundingDino Node | Florence-2 Replacement | Notes |
|-------------------|----------------------|-------|
| `GroundingDinoModelLoader` | `Florence2ModelLoader` | Use fp16 for better performance |
| `GroundingDinoDetect` | `Florence2Run` | Set task="object_detection" |
| `GroundDinoTextToMask` | `Florence2Run` + `Florence2toCoordinates` | Two-step process |
| `GroundingDinoSAMSegment` | `Florence2Run` + `Florence2toCoordinates` + `SAM2` | Three-node pipeline |

### Input Parameter Mappings

| GroundingDino Parameter | Florence-2 Equivalent | Default Value |
|------------------------|----------------------|---------------|
| `model_name` | `model` | "microsoft/florence-2-large" |
| `prompt` | `text_input` | "" |
| `threshold` | (confidence handled internally) | - |
| `box_threshold` | (handled by task) | - |

## Task Types

Florence-2 supports multiple tasks beyond object detection:

```python
SUPPORTED_TASKS = {
    "object_detection": "Detect objects and return bounding boxes",
    "dense_region_caption": "Generate captions for image regions",
    "region_proposal": "Propose regions of interest",
    "caption": "Generate image caption",
    "detailed_caption": "Generate detailed image description",
    "more_detailed_caption": "Generate very detailed description",
    "phrase_grounding": "Ground phrases to image regions",
    "referring_expression_comprehension": "Locate objects by description",
    "open_vocabulary_detection": "Detect using open vocabulary",
    "ocr": "Extract text from image",
    "ocr_with_region": "Extract text with bounding boxes"
}
```

## Common Workflow Patterns

### Pattern 1: Simple Object Detection

**Before:**
```
LoadImage → GroundingDinoModelLoader → GroundingDinoDetect → PreviewImage
```

**After:**
```
LoadImage → Florence2ModelLoader → Florence2Run → PreviewImage
```

### Pattern 2: Detection + Segmentation

**Before:**
```
LoadImage → GroundingDinoModelLoader → GroundingDinoSAMSegment → PreviewImage
            SAMModelLoader ────────────┘
```

**After:**
```
LoadImage → Florence2ModelLoader → Florence2Run → Florence2toCoordinates → SAM2 → PreviewImage
            SAMModelLoader ────────────────────────────────────────────────┘
```

### Pattern 3: Multi-Stage Detection

**Before:**
```
LoadImage → GroundingDino (Stage 1) → Filter → GroundingDino (Stage 2) → Output
```

**After:**
```
LoadImage → Florence2 (Stage 1) → Filter → Florence2 (Stage 2) → Output
```

## Quick Commands

### Install Florence-2
```bash
cd ComfyUI/custom_nodes && git clone https://github.com/kijai/ComfyUI-Florence2 && pip install -r ComfyUI-Florence2/requirements.txt
```

### Migrate Workflow
```bash
python migrate_workflow.py input.json output.json --pretty
```

### Test Installation
```python
from transformers import AutoProcessor, AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("microsoft/florence-2-base", trust_remote_code=True)
print("✅ Florence-2 installed successfully")
```

## Configuration Templates

### Optimized for Speed
```json
{
  "class_type": "Florence2ModelLoader",
  "inputs": {
    "model": "microsoft/florence-2-base",
    "precision": "fp16",
    "attention": "sdpa"
  }
}
```

### Optimized for Accuracy
```json
{
  "class_type": "Florence2ModelLoader",
  "inputs": {
    "model": "microsoft/florence-2-large",
    "precision": "fp32",
    "attention": "sdpa"
  }
}
```

### Optimized for Low Memory
```json
{
  "class_type": "Florence2ModelLoader",
  "inputs": {
    "model": "microsoft/florence-2-base",
    "precision": "int8",
    "attention": "sdpa"
  }
}
```

## Prompt Templates

### Generic Object Detection
```json
{
  "task": "object_detection",
  "text_input": "Detect all objects in the image"
}
```

### Specific Object Detection
```json
{
  "task": "object_detection",
  "text_input": "Detect person, car, and bicycle in the image"
}
```

### Region-Based Detection
```json
{
  "task": "phrase_grounding",
  "text_input": "<OD>person in red shirt</OD><OD>blue car</OD>"
}
```

### Caption + Detection
```json
{
  "task": "dense_region_caption",
  "text_input": ""
}
```

## Performance Targets

| Metric | Target | Method |
|--------|--------|--------|
| Inference Speed | <2s per image | Use base model + fp16 |
| Memory Usage | <2GB VRAM | Use fp16 or int8 |
| Accuracy | >90% mAP@0.5 | Use large model + proper prompts |
| Stability | 99%+ success | Use recommended config |

## Common Errors

| Error Message | Cause | Quick Fix |
|--------------|-------|-----------|
| "Unknown node type: Florence2ModelLoader" | Node not installed | Install custom node |
| "CUDA out of memory" | Insufficient VRAM | Use fp16 or base model |
| "Model not found" | Download failed | Check internet, pre-download model |
| "Invalid task type" | Wrong task name | Use supported task from list above |

## Resources

- **Migration Guide**: [GROUNDINGDINO_REPLACEMENT_GUIDE.md](GROUNDINGDINO_REPLACEMENT_GUIDE.md)
- **Technical Details**: [TECHNICAL_COMPARISON.md](TECHNICAL_COMPARISON.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Florence-2 Paper**: [arXiv:2311.06242](https://arxiv.org/abs/2311.06242)
- **ComfyUI Florence-2**: [GitHub](https://github.com/kijai/ComfyUI-Florence2)

## Version Compatibility

| Component | Minimum Version | Recommended |
|-----------|----------------|-------------|
| ComfyUI | Any recent | Latest |
| Python | 3.8+ | 3.10+ |
| PyTorch | 2.0+ | 2.1+ |
| Transformers | 4.35+ | Latest |
| CUDA | 11.8+ | 12.1+ |

---

**Quick Tip**: Always backup your workflow before migration! 💾
