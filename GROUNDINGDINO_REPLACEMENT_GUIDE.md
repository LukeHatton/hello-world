# GroundingDino Node Replacement Guide

## Problem Statement (问题说明)

GroundingDino nodes in ComfyUI workflows are known for:
- 不稳定性 (Instability issues)
- 低质量代码 (Low-quality code)
- 频繁需要排查 (Frequent troubleshooting required)
- 性能问题 (Performance problems)

## Recommended Alternatives (推荐替代方案)

### 1. Florence-2 (Best for General Object Detection)
**优点 (Advantages):**
- More stable and actively maintained
- Better integration with ComfyUI
- Supports multiple vision-language tasks
- Higher accuracy for object detection
- Faster inference speed
- Better memory management

**Node:** `Florence2ModelLoader` and `Florence2Run`

### 2. YOLO (Best for Real-time Detection)
**优点 (Advantages):**
- Industry-standard object detection
- Excellent performance and stability
- Multiple versions available (YOLOv5, YOLOv8, YOLOv9)
- Well-documented and supported
- Fast inference

**Node:** `YOLOv8Detect` or `UltralyticsDetectorProvider`

### 3. SAM (Segment Anything Model) with CLIP
**优点 (Advantages):**
- More accurate segmentation
- Better generalization
- Stable and well-maintained
- Can work with text prompts via CLIP

**Nodes:** `SAMModelLoader`, `CLIPTextEncode`, `SAMDetector`

## Migration Strategy (迁移策略)

### Step 1: Identify GroundingDino Nodes
Look for these node types in your workflow JSON:
- `GroundingDinoModelLoader`
- `GroundingDinoSAMSegment`
- `GroundDinoTextToMask`

### Step 2: Replace with Florence-2 (Recommended)

#### Before (GroundingDino):
```json
{
  "class_type": "GroundingDinoModelLoader",
  "inputs": {
    "model_name": "GroundingDINO_SwinB (938MB)"
  }
}
```

#### After (Florence-2):
```json
{
  "class_type": "Florence2ModelLoader",
  "inputs": {
    "model": "microsoft/florence-2-large",
    "precision": "fp16",
    "attention": "sdpa"
  }
}
```

### Step 3: Update Detection Nodes

#### Before (GroundingDino Detection):
```json
{
  "class_type": "GroundingDinoSAMSegment",
  "inputs": {
    "prompt": "person, car, dog",
    "threshold": 0.3
  }
}
```

#### After (Florence-2 Detection):
```json
{
  "class_type": "Florence2Run",
  "inputs": {
    "task": "object_detection",
    "text_input": "person, car, dog",
    "max_new_tokens": 1024
  }
}
```

## Benefits of Migration (迁移优势)

1. **稳定性提升 (Improved Stability)**: Florence-2 has fewer runtime errors
2. **更好的性能 (Better Performance)**: Faster inference and lower memory usage
3. **更高质量 (Higher Quality)**: Better maintained codebase
4. **更好的支持 (Better Support)**: Active community and documentation
5. **兼容性 (Compatibility)**: Better integration with latest ComfyUI versions

## Installation Requirements

For Florence-2:
```bash
# Install required custom nodes
cd ComfyUI/custom_nodes
git clone https://github.com/kijai/ComfyUI-Florence2
pip install -r ComfyUI-Florence2/requirements.txt
```

For YOLO:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-Ultralytics
pip install ultralytics
```

## Example Complete Workflow Replacement

See `example_workflow_before.json` and `example_workflow_after.json` for complete working examples.

## Testing Your Migration

1. Load your modified workflow in ComfyUI
2. Test with the same input images
3. Compare detection results
4. Verify memory usage is acceptable
5. Check inference speed improvements

## Troubleshooting

### Issue: Florence-2 not found
**Solution:** Install the Florence-2 custom node from the ComfyUI Manager

### Issue: Different detection results
**Solution:** Adjust the confidence threshold and prompt format

### Issue: Memory errors
**Solution:** Use fp16 precision or smaller model variant

## Conclusion

Replacing GroundingDino with Florence-2 or YOLO provides:
- ✅ Better stability
- ✅ Improved performance  
- ✅ Easier maintenance
- ✅ Better results

推荐使用 Florence-2 作为 GroundingDino 的替代方案！
