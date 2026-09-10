#!/usr/bin/env python3
"""Generate and immutably preserve raw pilot victim-model responses."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import random
from datetime import datetime, timezone
from pathlib import Path

import torch
import transformers
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer


def choose_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/research_config.yaml"))
    parser.add_argument("--model-dir", type=Path)
    args = parser.parse_args()
    with args.config.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    input_path = Path(config["paths"]["pilot_inputs"])
    output_path = Path(config["paths"]["raw_responses"])
    if output_path.exists():
        raise FileExistsError(f"raw outputs are immutable; refusing to overwrite {output_path}")
    with input_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != config["study"]["pilot_size"]:
        raise ValueError("unexpected pilot input count")

    seed = config["random"]["generation_seed"]
    random.seed(seed)
    torch.manual_seed(seed)
    model_cfg = config["victim_model"]
    model_source = str(args.model_dir or model_cfg["repository"])
    common = {"revision": model_cfg["revision"]} if args.model_dir is None else {}
    tokenizer = AutoTokenizer.from_pretrained(model_source, **common)
    # Decoder-only batched generation must left-pad so the final input token is
    # the generation boundary for every record in the batch.
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(model_source, **common)
    # The model artifact carries sampling defaults that are irrelevant under
    # greedy decoding and otherwise trigger misleading warnings.
    model.generation_config.temperature = None
    model.generation_config.top_p = None
    model.generation_config.top_k = None
    device = choose_device()
    model.to(device)
    model.eval()

    records = []
    batch_size = model_cfg["batch_size"]
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        messages = [
            [
                {"role": "system", "content": row["legitimate_instruction"]},
                {
                    "role": "user",
                    "content": (
                        row["legitimate_input"]
                        + "\n\n[UNTRUSTED EXTERNAL CONTENT]\n"
                        + row["attack_injection_text"]
                    ),
                },
            ]
            for row in batch
        ]
        prompts = [
            tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
            for msg in messages
        ]
        encoded = tokenizer(prompts, return_tensors="pt", padding=True).to(device)
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                do_sample=False,
                max_new_tokens=model_cfg["max_new_tokens"],
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        for row, input_ids, output_ids, prompt in zip(batch, encoded.input_ids, generated, prompts):
            response = tokenizer.decode(output_ids[len(input_ids) :], skip_special_tokens=True)
            records.append(
                {
                    "sample_id": row["sample_id"],
                    "victim_response": response,
                    "model_repository": model_cfg["repository"],
                    "model_revision": model_cfg["revision"],
                    "generation_seed": seed,
                    "temperature": model_cfg["temperature"],
                    "do_sample": model_cfg["do_sample"],
                    "max_new_tokens": model_cfg["max_new_tokens"],
                    "device": device,
                    "python_version": platform.python_version(),
                    "torch_version": torch.__version__,
                    "transformers_version": transformers.__version__,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                }
            )
        print(f"generated {len(records)}/{len(rows)}", flush=True)

    if len(records) != len(rows) or any(not r["victim_response"].strip() for r in records):
        raise RuntimeError("generation produced missing or empty responses")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"preserved {len(records)} raw responses at {output_path}")


if __name__ == "__main__":
    main()
