"""Judge AI model for detecting human vs AI responses"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re
import logging
from typing import Dict, Optional
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

logger = logging.getLogger(__name__)

class JudgeAI:
    """AI Judge that determines if responses are human or AI-generated"""
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """Initialize the Judge AI model
        
        Args:
            model_name: HuggingFace model name to use
            device: Device to run model on ('cuda', 'cpu', or 'auto')
        """
        self.model_name = model_name or Config.JUDGE_MODEL_NAME
        
        # Determine device
        if device:
            self.device = device
        elif Config.USE_GPU == 'auto':
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = Config.USE_GPU
            
        logger.info(f"Initializing JudgeAI with model: {self.model_name} on device: {self.device}")
        
        try:
            # Load tokenizer with trust_remote_code for models that require it
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=Config.MODEL_CACHE_DIR,
                trust_remote_code=True
            )
            
            # Set padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate settings for device
            if self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    cache_dir=Config.MODEL_CACHE_DIR,
                    trust_remote_code=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    cache_dir=Config.MODEL_CACHE_DIR,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                self.model = self.model.to(self.device)
                
            self.model.eval()
            logger.info("JudgeAI model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load JudgeAI model: {str(e)}")
            raise
    
    def judge_response(self, prompt: str, response: str, style_cloak: Optional[str] = None) -> Dict:
        """Judge if a response is human or AI-generated
        
        Args:
            prompt: The original prompt
            response: The response to judge
            style_cloak: Optional style modifier applied
            
        Returns:
            Dictionary with 'human_prob' (0-1) and 'reasoning' keys
        """
        # Construct the judge prompt
        judge_prompt = self._construct_judge_prompt(prompt, response, style_cloak)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                judge_prompt,
                return_tensors="pt",
                max_length=2048,
                truncation=True,
                padding=True
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            # Parse the judgment
            result = self.parse_judgment(generated_text)
            
            # Log for debugging
            logger.debug(f"Judge input: {prompt[:100]}...")
            logger.debug(f"Judge output: {generated_text}")
            logger.debug(f"Parsed result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in judge_response: {str(e)}")
            # Return neutral judgment on error
            return {
                "human_prob": 0.5,
                "reasoning": "Unable to make determination due to processing error."
            }
    
    def _construct_judge_prompt(self, prompt: str, response: str, style_cloak: Optional[str] = None) -> str:
        """Construct the prompt for the judge model"""
        
        style_note = f"\nNote: A style modifier was applied: {style_cloak}" if style_cloak else ""
        
        judge_prompt = f"""You are an expert at detecting whether text was written by a human or an AI assistant.

Analyze the following response to determine if it was written by a human or AI.

Original Prompt: {prompt}

Response to Analyze: {response}
{style_note}

Consider these factors:
- Writing style and natural flow
- Presence of personal experiences or emotions
- Imperfections, typos, or informal language
- Overly structured or formulaic responses
- Hedging language or uncertainty markers
- Specific details vs. generic statements

Provide your analysis in exactly this format:
HUMAN_PROB: [number between 0 and 100]
REASONING: [2-3 sentences explaining your judgment]

Your response:"""
        
        return judge_prompt
    
    def parse_judgment(self, raw_output: str) -> Dict:
        """Parse the model's judgment output
        
        Args:
            raw_output: Raw text from the model
            
        Returns:
            Dictionary with human_prob (0-1 float) and reasoning
        """
        result = {
            "human_prob": 0.5,
            "reasoning": "Unable to parse model output"
        }
        
        try:
            # Look for HUMAN_PROB pattern
            prob_match = re.search(r'HUMAN_PROB:\s*(\d+(?:\.\d+)?)', raw_output, re.IGNORECASE)
            if prob_match:
                prob_value = float(prob_match.group(1))
                # Convert to 0-1 range if given as percentage
                if prob_value > 1:
                    prob_value = prob_value / 100.0
                result["human_prob"] = min(max(prob_value, 0.0), 1.0)
            
            # Look for REASONING pattern
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n|$)', raw_output, re.IGNORECASE | re.DOTALL)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
                # Clean up the reasoning text
                reasoning = re.sub(r'\s+', ' ', reasoning)  # Replace multiple spaces
                result["reasoning"] = reasoning[:500]  # Limit length
            
            # Fallback: if no structured format found, try to extract meaning
            if result["reasoning"] == "Unable to parse model output":
                # Look for keywords indicating human or AI
                lower_output = raw_output.lower()
                if "human" in lower_output and "ai" not in lower_output:
                    result["human_prob"] = 0.7
                    result["reasoning"] = "Response appears to be human-written based on analysis."
                elif "ai" in lower_output and "human" not in lower_output:
                    result["human_prob"] = 0.3
                    result["reasoning"] = "Response appears to be AI-generated based on analysis."
                else:
                    result["reasoning"] = raw_output[:200] if raw_output else "No judgment provided"
                    
        except Exception as e:
            logger.error(f"Error parsing judgment: {str(e)}")
            
        return result
    
    def batch_judge(self, examples: list) -> list:
        """Judge multiple examples in batch for efficiency
        
        Args:
            examples: List of (prompt, response) tuples
            
        Returns:
            List of judgment dictionaries
        """
        results = []
        for prompt, response in examples:
            result = self.judge_response(prompt, response)
            results.append(result)
        return results
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "model_size_mb": sum(p.numel() * p.element_size() for p in self.model.parameters()) / 1024 / 1024
        }