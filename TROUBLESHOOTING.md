# Migration Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Florence-2 Custom Node Not Found

**Symptoms:**
- Error: "Unknown node type: Florence2ModelLoader"
- Workflow fails to load

**Solution:**
```bash
# Install Florence-2 custom node
cd ComfyUI/custom_nodes
git clone https://github.com/kijai/ComfyUI-Florence2
cd ComfyUI-Florence2
pip install -r requirements.txt

# Restart ComfyUI
```

### Issue 2: Model Download Failed

**Symptoms:**
- Error: "Could not download microsoft/florence-2-large"
- Connection timeout

**Solution:**
```python
# Pre-download model manually
from transformers import AutoProcessor, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "microsoft/florence-2-large",
    cache_dir="/path/to/models",  # Specify cache location
    trust_remote_code=True
)
```

Or use the base model (smaller, faster download):
```python
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/florence-2-base",
    trust_remote_code=True
)
```

### Issue 3: CUDA Out of Memory

**Symptoms:**
- Error: "CUDA out of memory"
- System freezes

**Solution:**
1. Use fp16 precision instead of fp32:
```json
{
  "class_type": "Florence2ModelLoader",
  "inputs": {
    "model": "microsoft/florence-2-base",  // Use base model
    "precision": "fp16",  // Use half precision
    "attention": "sdpa"
  }
}
```

2. Reduce batch size
3. Enable model offloading
4. Use smaller model variant (florence-2-base)

### Issue 4: Different Detection Results

**Symptoms:**
- Objects detected differently than GroundingDino
- Missing some detections

**Solution:**
Adjust the prompt format:

**GroundingDino format:**
```
"prompt": "person, car, dog"
```

**Florence-2 format (more descriptive):**
```
"text_input": "Detect person, car, and dog in the image"
```

Or use task-specific prompts:
```
"text_input": "What objects are in this image? Include person, car, dog"
```

### Issue 5: SAM Integration Issues

**Symptoms:**
- Segmentation not working after detection
- Error connecting Florence-2 to SAM

**Solution:**
Ensure you use the intermediate node:
```json
{
  "florence2_node": {
    "class_type": "Florence2Run",
    "inputs": {...}
  },
  "coords_node": {
    "class_type": "Florence2toCoordinates",  // This is required!
    "inputs": {
      "florence2_result": ["florence2_node", 0],
      "index": "all"
    }
  },
  "sam_node": {
    "class_type": "SAM2",
    "inputs": {
      "coordinates": ["coords_node", 0],  // Use coords, not florence2 directly
      ...
    }
  }
}
```

### Issue 6: Slow Inference

**Symptoms:**
- Much slower than expected
- High memory usage

**Solution:**
1. Enable model caching:
```json
{
  "class_type": "Florence2ModelLoader",
  "inputs": {
    "keep_model_loaded": true  // Keep in VRAM between runs
  }
}
```

2. Use optimized attention:
```json
{
  "attention": "sdpa"  // Scaled Dot Product Attention (faster)
}
```

3. Reduce beam search:
```json
{
  "class_type": "Florence2Run",
  "inputs": {
    "num_beams": 1,  // Faster but less accurate
    "do_sample": false
  }
}
```

### Issue 7: Migration Script Errors

**Symptoms:**
- Script fails to run
- JSON parsing errors

**Solution:**
1. Validate input JSON:
```bash
python -m json.tool input_workflow.json
```

2. Check file encoding:
```bash
file -i input_workflow.json
# Should show: utf-8
```

3. Run with debug output:
```bash
python migrate_workflow.py input.json output.json --pretty
```

### Issue 8: Workflow Connections Broken

**Symptoms:**
- Nodes disconnected after migration
- Missing inputs

**Solution:**
The migration script preserves connections using node IDs. Check that:
1. Original workflow has valid connections
2. Node IDs are properly formatted
3. Review the migrated JSON structure

Manual fix if needed:
```json
{
  "node_id": {
    "inputs": {
      "image": ["source_node_id", output_index]
    }
  }
}
```

### Issue 9: Hugging Face Authentication

**Symptoms:**
- Error: "Repo model microsoft/florence-2-large is gated"
- Authentication required

**Solution:**
```bash
# Login to Hugging Face
pip install huggingface_hub
huggingface-cli login

# Or set token in environment
export HF_TOKEN="your_token_here"
```

### Issue 10: Custom Prompt Not Working

**Symptoms:**
- Florence-2 ignoring custom prompts
- Generic detections only

**Solution:**
Use proper task and prompt combination:

**For specific object detection:**
```json
{
  "task": "object_detection",
  "text_input": "Detect the following objects: cat, dog, person"
}
```

**For open-ended detection:**
```json
{
  "task": "dense_region_caption",
  "text_input": ""
}
```

**For phrase grounding:**
```json
{
  "task": "phrase_grounding",
  "text_input": "<OD>person wearing red shirt</OD>"
}
```

## Performance Optimization Tips

### 1. Model Selection
- **florence-2-base**: Fast, lower accuracy (~230MB)
- **florence-2-large**: Slower, higher accuracy (~770MB)

### 2. Precision Settings
- **fp32**: Highest accuracy, slowest, 2x memory
- **fp16**: Good balance (recommended)
- **int8**: Fastest, lowest memory, reduced accuracy

### 3. Batch Processing
```python
# Process multiple images efficiently
for batch in image_batches:
    results = model.process_batch(batch)  # Process together
```

### 4. Memory Management
```python
import torch

# Clear cache between runs
torch.cuda.empty_cache()

# Use context manager
with torch.inference_mode():
    result = model(input)
```

## Validation Checklist

Before considering migration complete:

- [ ] Workflow loads without errors
- [ ] All nodes have proper connections
- [ ] Test with sample images
- [ ] Compare output quality with original
- [ ] Check memory usage is acceptable
- [ ] Verify inference speed
- [ ] Test error handling (invalid inputs)
- [ ] Document any parameter changes
- [ ] Update workflow version/notes

## Getting Help

If issues persist:

1. **Check logs:**
   ```bash
   # ComfyUI logs are usually in:
   ComfyUI/output/
   ```

2. **Enable debug mode:**
   Add to your Florence-2 node:
   ```json
   "verbose": true
   ```

3. **Test with minimal workflow:**
   Create a simple 2-3 node workflow to isolate the issue

4. **Community support:**
   - ComfyUI Discord
   - Florence-2 GitHub issues
   - ComfyUI Reddit

## Rollback Procedure

If you need to revert:

1. Keep original workflow backup
2. Uninstall Florence-2 if needed:
   ```bash
   cd ComfyUI/custom_nodes
   rm -rf ComfyUI-Florence2
   ```
3. Restore original workflow
4. Reinstall GroundingDino (not recommended)

## Success Indicators

You've successfully migrated when:

- ✅ No errors in ComfyUI console
- ✅ Workflow completes without crashes
- ✅ Detection quality is good or better
- ✅ Inference time is acceptable
- ✅ Memory usage is stable
- ✅ Can process batch jobs reliably

---

**Remember:** Migration is iterative. Don't expect perfect results on first try. Test, adjust, and optimize!
