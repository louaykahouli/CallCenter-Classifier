import os
import torch
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer
import argparse
import json


def is_state_dict(path):
    try:
        data = torch.load(path, map_location='cpu')
        # Common heuristic: state_dict is a dict of tensors and/or nested dicts
        if isinstance(data, dict) and any(isinstance(v, torch.Tensor) for v in data.values()):
            return True
        # HF saved model might be a dict with 'model_state_dict' key
        if isinstance(data, dict) and 'model_state_dict' in data:
            return True
        return False
    except Exception:
        return False


def load_and_save(pt_path, output_dir, model_name='distilbert-base-multilingual-cased'):
    os.makedirs(output_dir, exist_ok=True)

    if is_state_dict(pt_path):
        print(f"Detected a state_dict in {pt_path} - loading into a {model_name} architecture...")
        # Load base config and model
        config = AutoConfig.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_config(config)

        # Load the state dict
        data = torch.load(pt_path, map_location='cpu')
        # support both raw state_dict and wrapped dicts
        if 'model_state_dict' in data:
            state_dict = data['model_state_dict']
        elif 'state_dict' in data:
            state_dict = data['state_dict']
        else:
            state_dict = data

        # Try to load state dict
        missing, unexpected = model.load_state_dict(state_dict, strict=False)
        print("Missing keys:", missing)
        print("Unexpected keys:", unexpected)

        # Save the model in Hugging Face format
        print(f"Saving HF model to {output_dir} ...")
        model.save_pretrained(output_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(output_dir)

        # Save a minimal label mapping placeholder if not present
        mapping_path = os.path.join(output_dir, 'label_mappings.json')
        if not os.path.exists(mapping_path):
            with open(mapping_path, 'w') as f:
                json.dump({'label2id': {}, 'id2label': {}}, f)
        print("Conversion complete.")
    else:
        # Maybe the .pt is a full HF checkpoint saved with torch.save(model)
        try:
            obj = torch.load(pt_path, map_location='cpu')
            # If obj is a nn.Module, save it via state_dict
            if hasattr(obj, 'state_dict'):
                print("Detected a full model object; extracting state_dict...")
                state_dict = obj.state_dict()
                config = AutoConfig.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_config(config)
                missing, unexpected = model.load_state_dict(state_dict, strict=False)
                print("Missing keys:", missing)
                print("Unexpected keys:", unexpected)
                model.save_pretrained(output_dir)
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                tokenizer.save_pretrained(output_dir)
                print("Saved converted model to HF format.")
                return
        except Exception as e:
            print("Not a PyTorch model object:", e)

        raise RuntimeError("Unrecognized .pt format. If the file is a HF model, ensure you saved it using `model.save_pretrained()` or pass a state_dict.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a .pt file into HF model directory')
    parser.add_argument('pt_path', help='Path to the .pt file (e.g., data/processed/optimizer.pt)')
    parser.add_argument('--out', '-o', default='models/transformer', help='Output directory for HF model files')
    parser.add_argument('--model-name', default='distilbert-base-multilingual-cased', help='Base model architecture if only state_dict is provided')
    args = parser.parse_args()

    load_and_save(args.pt_path, args.out, args.model_name)
