#!/usr/bin/env python3
"""
ComfyUI Workflow Migration Script
Automatically replaces GroundingDino nodes with Florence-2 nodes

Usage:
    python migrate_workflow.py input_workflow.json output_workflow.json
"""

import json
import sys
import argparse
from typing import Dict, Any

# Constants
DEFAULT_SEED = 42
DEFAULT_PROMPT = "Detect objects in the image"


def format_detection_prompt(prompt: str) -> str:
    """
    Format a prompt for Florence-2 object detection.
    
    Args:
        prompt: The raw prompt from GroundingDino (e.g., "person, car, dog")
    
    Returns:
        A formatted prompt suitable for Florence-2
    """
    if not prompt:
        return DEFAULT_PROMPT
    return f"Detect {prompt} in the image"


def migrate_grounding_dino_model_loader(node: Dict[str, Any]) -> Dict[str, Any]:
    """Replace GroundingDinoModelLoader with Florence2ModelLoader"""
    return {
        "class_type": "Florence2ModelLoader",
        "inputs": {
            "model": "microsoft/florence-2-large",
            "precision": "fp16",
            "attention": "sdpa"
        }
    }


def migrate_grounding_dino_detect(node: Dict[str, Any]) -> Dict[str, Any]:
    """Replace GroundingDino detection nodes with Florence2Run"""
    inputs = node.get("inputs", {})
    prompt = inputs.get("prompt", inputs.get("text_prompt", ""))
    
    if not prompt:
        print("  ⚠ Warning: No prompt found, using default prompt")
    
    new_node = {
        "class_type": "Florence2Run",
        "inputs": {
            "task": "object_detection",
            "text_input": format_detection_prompt(prompt),
            "fill_mask": True,
            "max_new_tokens": 1024,
            "num_beams": 3,
            "do_sample": True,
            "output_mask_select": "",
            "seed": DEFAULT_SEED,
            "keep_model_loaded": True
        }
    }
    
    # Preserve connections to model and image
    if "dino_model" in inputs:
        new_node["inputs"]["model"] = inputs["dino_model"]
    if "image" in inputs:
        new_node["inputs"]["image"] = inputs["image"]
    
    return new_node


def migrate_grounding_dino_segment(node: Dict[str, Any], workflow: Dict[str, Any], node_id: str) -> Dict[str, Dict[str, Any]]:
    """
    Replace GroundingDinoSAMSegment with Florence2Run + Florence2toCoordinates + SAM2
    Returns multiple nodes to replace the single GroundingDino node
    """
    inputs = node.get("inputs", {})
    prompt = inputs.get("prompt", "")
    
    if not prompt:
        print("  ⚠ Warning: No prompt found in segment node, using default")
    
    # Create three new nodes to replace the single GroundingDino segment node
    nodes = {}
    
    # Node 1: Florence2Run for detection
    florence_node_id = f"{node_id}_florence"
    nodes[florence_node_id] = {
        "class_type": "Florence2Run",
        "inputs": {
            "task": "object_detection",
            "text_input": format_detection_prompt(prompt),
            "fill_mask": True,
            "max_new_tokens": 1024,
            "num_beams": 3,
            "do_sample": True,
            "output_mask_select": "",
            "seed": DEFAULT_SEED,
            "keep_model_loaded": True
        }
    }
    
    # Preserve image input
    if "image" in inputs:
        nodes[florence_node_id]["inputs"]["image"] = inputs["image"]
    if "dino_model" in inputs:
        # Connect to Florence model instead
        nodes[florence_node_id]["inputs"]["model"] = inputs["dino_model"]
    
    # Node 2: Florence2toCoordinates
    coords_node_id = f"{node_id}_coords"
    nodes[coords_node_id] = {
        "class_type": "Florence2toCoordinates",
        "inputs": {
            "florence2_result": [florence_node_id, 0],
            "index": "all"
        }
    }
    
    # Node 3: SAM2 for final segmentation
    sam_node_id = node_id  # Keep the original node ID for the final output
    nodes[sam_node_id] = {
        "class_type": "SAM2",
        "inputs": {
            "coordinates": [coords_node_id, 0],
            "individual_objects": True
        }
    }
    
    # Preserve SAM model and image connections
    if "sam_model" in inputs:
        nodes[sam_node_id]["inputs"]["sam_model"] = inputs["sam_model"]
    if "image" in inputs:
        nodes[sam_node_id]["inputs"]["image"] = inputs["image"]
    
    return nodes


def migrate_workflow(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate a ComfyUI workflow from GroundingDino to Florence-2
    """
    new_workflow = {}
    nodes_to_add = []
    
    for node_id, node in workflow.items():
        class_type = node.get("class_type", "")
        
        if class_type == "GroundingDinoModelLoader":
            print(f"✓ Migrating {node_id}: GroundingDinoModelLoader → Florence2ModelLoader")
            new_workflow[node_id] = migrate_grounding_dino_model_loader(node)
            
        elif class_type in ["GroundingDinoDetect", "GroundDinoTextToMask"]:
            print(f"✓ Migrating {node_id}: {class_type} → Florence2Run")
            new_workflow[node_id] = migrate_grounding_dino_detect(node)
            
        elif class_type == "GroundingDinoSAMSegment":
            print(f"✓ Migrating {node_id}: GroundingDinoSAMSegment → Florence2Run + SAM2 pipeline")
            migrated_nodes = migrate_grounding_dino_segment(node, workflow, node_id)
            # Add the new nodes
            for new_id, new_node in migrated_nodes.items():
                if new_id == node_id:
                    new_workflow[new_id] = new_node
                else:
                    nodes_to_add.append((new_id, new_node))
        else:
            # Keep other nodes unchanged
            new_workflow[node_id] = node
    
    # Add any additional nodes that were created during migration
    for new_id, new_node in nodes_to_add:
        new_workflow[new_id] = new_node
    
    return new_workflow


def main():
    parser = argparse.ArgumentParser(
        description="Migrate ComfyUI workflow from GroundingDino to Florence-2"
    )
    parser.add_argument("input", help="Input workflow JSON file")
    parser.add_argument("output", help="Output workflow JSON file")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print the output JSON"
    )
    
    args = parser.parse_args()
    
    try:
        # Load input workflow
        print(f"Loading workflow from {args.input}...")
        with open(args.input, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        print(f"Found {len(workflow)} nodes in workflow")
        
        # Migrate workflow
        print("\nMigrating workflow...")
        migrated_workflow = migrate_workflow(workflow)
        
        # Save output workflow
        print(f"\nSaving migrated workflow to {args.output}...")
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.pretty:
                json.dump(migrated_workflow, f, indent=2, ensure_ascii=False)
            else:
                json.dump(migrated_workflow, f, ensure_ascii=False)
        
        print(f"\n✅ Migration complete! {len(migrated_workflow)} nodes in new workflow")
        print("\nNext steps:")
        print("1. Install Florence-2 custom node in ComfyUI")
        print("2. Load the migrated workflow in ComfyUI")
        print("3. Test with your images")
        print("4. Adjust parameters as needed")
        
        return 0
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find input file '{args.input}'")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in input file: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
