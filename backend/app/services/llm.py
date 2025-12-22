from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from app.core.config import settings
from app.core.logger import logger


class LLMService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = settings.LLM_MODEL
    
    def load_model(self):
        if self.model is None:
            logger.info(f"Loading LLM model: {self.model_name}")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                logger.info("LLM model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load LLM model: {e}")
                logger.info("Using fallback: returning context directly")
        return self.model
    
    def generate(self, prompt: str, max_length: int = 512) -> str:
        try:
            model = self.load_model()
            if model is None:
                chunks = prompt.split("\n\n")
                if len(chunks) > 1:
                    return f"Based on the provided context: {chunks[1][:200]}..."
                return "LLM model not available. Please check configuration."
            
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=min(max_length, inputs["input_ids"].shape[1] + 200),
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = response[len(prompt):].strip()
            return answer if answer else "I couldn't generate a response. Please try rephrasing your question."
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            chunks = prompt.split("\n\n")
            if len(chunks) > 1:
                return f"Based on the provided context: {chunks[1][:200]}..."
            return f"Error generating response: {str(e)}"


llm_service = LLMService()

