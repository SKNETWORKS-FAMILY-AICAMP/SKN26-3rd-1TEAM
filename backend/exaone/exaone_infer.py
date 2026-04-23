from runpod_flash import Endpoint
from common.runpod import (
    RUNPOD_SUB_DATACENTER,
    RUNPOD_SUB_GPU,
    get_runpod_sub_volume,
)


@Endpoint(
    name="exaone-sub",
    gpu=RUNPOD_SUB_GPU,
    datacenter=RUNPOD_SUB_DATACENTER,
    volume=get_runpod_sub_volume(),
    execution_timeout_ms=0,
    workers=(1, 1),
    idle_timeout=300,
    dependencies=["torch", "transformers>=4.43"],
)
async def exaone_sub_infer(data: dict):
    import os
    import gc
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    inputs = None
    output = None

    def generate_in_chunks(
        model,
        tokenizer,
        full_prompt: str,
        temperature: float,
        total_max_new_tokens: int = 8192,
        chunk_size: int = 512,
        prompt_max_length: int = 4096,
    ) -> str:
        generated_text = ""
        current_prompt = full_prompt
        total_generated = 0
        do_sample = temperature > 0.0

        while total_generated < total_max_new_tokens:
            current_chunk = min(chunk_size, total_max_new_tokens - total_generated)

            local_inputs = tokenizer(
                current_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=prompt_max_length,
            )
            local_inputs = {k: v.to("cuda") for k, v in local_inputs.items()}

            generate_kwargs = {
                **local_inputs,
                "max_new_tokens": current_chunk,
                "do_sample": do_sample,
                "pad_token_id": tokenizer.pad_token_id,
                "eos_token_id": tokenizer.eos_token_id,
                "use_cache": False,
            }

            if do_sample:
                generate_kwargs["temperature"] = temperature

            with torch.inference_mode():
                local_output = model.generate(**generate_kwargs)

            prompt_length = local_inputs["input_ids"].shape[1]
            new_tokens = local_output[0][prompt_length:].detach().cpu()

            # 종료 토큰만 나온 경우 방지
            if new_tokens.numel() == 0:
                del local_inputs
                del local_output
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                break

            new_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
            if not new_text.strip():
                del local_inputs
                del local_output
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                break

            generated_text += new_text
            total_generated += len(new_tokens)

            # 다음 루프용 프롬프트 갱신
            current_prompt = full_prompt + generated_text

            # 메모리 정리
            del new_tokens
            del local_inputs
            del local_output
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        return generated_text

    try:
        model_path = "/runpod-volume/exaone-3.5-7.8b"

        if not os.path.exists(model_path):
            return {"ok": False, "error": "model path not found"}

        global_state = globals()
        tokenizer = global_state.get("_tokenizer")
        model = global_state.get("_model")

        if tokenizer is None:
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                local_files_only=True,
                use_fast=False,
            )
            if tokenizer.pad_token_id is None:
                tokenizer.pad_token_id = tokenizer.eos_token_id
            global_state["_tokenizer"] = tokenizer

        if model is None:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                local_files_only=True,
                device_map="auto",
            )
            model.eval()
            global_state["_model"] = model

        input_data = data["input"]
        messages = input_data["messages"]
        full_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        temperature = float(input_data.get("temperature", 0.7))

        # 총 목표 길이는 유지하되, 내부적으로 쪼개서 생성
        total_max_new_tokens = int(input_data.get("max_new_tokens", 8192))

        text = generate_in_chunks(
            model=model,
            tokenizer=tokenizer,
            full_prompt=full_prompt,
            temperature=temperature,
            total_max_new_tokens=total_max_new_tokens,
            chunk_size=512,  # 256~512부터 시작 추천
            prompt_max_length=4096,  # 너무 길어지면 앞부분 잘림
        )

        return {"ok": True, "text": text}

    except Exception as e:
        return {"ok": False, "error": str(e)}

    finally:
        try:
            del inputs
        except Exception:
            pass

        try:
            del output
        except Exception:
            pass

        try:
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
