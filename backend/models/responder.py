"""Responder AI model for generating human-like responses"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
from typing import Dict, Optional
import random
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

logger = logging.getLogger(__name__)

class ResponderAI:
    """AI Responder that generates responses to prompts, trying to mimic human writing"""
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """Initialize the Responder AI model
        
        Args:
            model_name: HuggingFace model name to use (should be different from Judge)
            device: Device to run model on ('cuda', 'cpu', or 'auto')
        """
        self.model_name = model_name or Config.RESPONDER_MODEL_NAME
        
        # Determine device
        if device:
            self.device = device
        elif Config.USE_GPU == 'auto':
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = Config.USE_GPU
            
        logger.info(f"Initializing ResponderAI with model: {self.model_name} on device: {self.device}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=Config.MODEL_CACHE_DIR,
                trust_remote_code=True
            )
            
            # Set padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate settings
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
            logger.info("ResponderAI model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load ResponderAI model: {str(e)}")
            raise
    
    def generate_response(self, 
                         prompt: str, 
                         style_cloak: Optional[str] = None,
                         temperature: Optional[float] = None,
                         max_length: Optional[int] = None) -> str:
        """Generate a response to a prompt
        
        Args:
            prompt: The prompt to respond to
            style_cloak: Optional style modifier to apply
            temperature: Generation temperature (higher = more creative)
            max_length: Maximum response length
            
        Returns:
            Generated response string
        """
        # Set generation parameters
        temp = temperature if temperature is not None else random.uniform(0.7, 1.0)
        max_tokens = max_length if max_length is not None else Config.MAX_RESPONSE_LENGTH
        
        # Apply style cloak if provided
        if style_cloak:
            generation_prompt = self._apply_style_cloak(prompt, style_cloak)
        else:
            generation_prompt = self._construct_response_prompt(prompt)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                generation_prompt,
                return_tensors="pt",
                max_length=1024,
                truncation=True,
                padding=True
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temp,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            # Post-process to make more human-like
            response = self._humanize_response(generated_text, style_cloak)
            
            logger.debug(f"Generated response for prompt: {prompt[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            # Return a simple fallback response
            return self._get_fallback_response(prompt)
    
    def _construct_response_prompt(self, prompt: str) -> str:
        """Construct the prompt for response generation"""
        
        # Randomly choose a persona to make responses more varied
        personas = [
            "You are a helpful assistant responding naturally and conversationally.",
            "You are responding in a casual, friendly manner.",
            "You are answering questions with enthusiasm and personality.",
            "You are providing thoughtful, detailed responses.",
        ]
        
        selected_persona = random.choice(personas)
        
        return f"""{selected_persona}

User: {prompt}
Assistant:"""
    
    def _apply_style_cloak(self, prompt: str, style_cloak: str) -> str:
        """Apply a style cloak to modify generation behavior"""
        
        # Get style cloak instructions from config
        from backend.style_cloaks import STYLE_CLOAKS
        
        cloak_config = STYLE_CLOAKS.get(style_cloak, {})
        ai_modification = cloak_config.get('ai_modification', '')
        
        return f"""Generate a response with these style modifications: {ai_modification}

User: {prompt}
Assistant:"""
    
    def _humanize_response(self, response: str, style_cloak: Optional[str] = None) -> str:
        """Post-process response to make it more human-like"""
        
        # Clean up the response
        response = response.strip()
        
        # Remove any "Assistant:" or similar prefixes if present
        prefixes_to_remove = ['Assistant:', 'AI:', 'Response:', 'Answer:']
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Randomly add human-like elements
        if not style_cloak and random.random() < 0.3:
            # Add occasional hesitation markers
            hesitations = ['Well, ', 'So, ', 'Actually, ', 'You know, ', 'I think ']
            response = random.choice(hesitations) + response[0].lower() + response[1:]
        
        if not style_cloak and random.random() < 0.1:
            # Add occasional filler words
            fillers = [' kind of ', ' sort of ', ' like ', ' basically ']
            words = response.split()
            if len(words) > 10:
                insert_pos = random.randint(3, min(10, len(words)-2))
                words[insert_pos] = words[insert_pos] + random.choice(fillers)
                response = ' '.join(words)
        
        # Limit response length to seem more natural
        sentences = response.split('. ')
        if len(sentences) > 5:
            # Keep a random number of sentences between 2-5
            num_sentences = random.randint(2, 5)
            response = '. '.join(sentences[:num_sentences])
            if not response.endswith('.'):
                response += '.'
        
        return response
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Generate a simple fallback response if model fails"""
        
        fallback_responses = [
            "That's an interesting question. Let me think about it...",
            "I'm not entirely sure, but here's what I think...",
            "Hmm, that's a tough one to answer definitively.",
            "From what I understand, this is a complex topic.",
            "I'd need to think more about this to give you a complete answer.",
        ]
        
        # Try to generate something relevant based on keywords
        if "?" in prompt:
            return random.choice(fallback_responses)
        elif any(word in prompt.lower() for word in ['explain', 'describe', 'tell']):
            return "Let me try to explain this as I understand it..."
        elif any(word in prompt.lower() for word in ['write', 'create', 'make']):
            return "Here's my attempt at that..."
        else:
            return random.choice(fallback_responses)
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "model_size_mb": sum(p.numel() * p.element_size() for p in self.model.parameters()) / 1024 / 1024
        }