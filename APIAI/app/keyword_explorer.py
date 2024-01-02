import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification


class ModelKeywordsExplorer:

    def __init__(self, model_path):
        tag2idx = {'B': 0, 'I': 1, 'O': 2}
        self.model = AutoModelForTokenClassification.from_pretrained(model_path, num_labels=len(tag2idx))
        self.tag2idx = tag2idx
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model.to("cuda")
        self.model.share_memory()

    def model_generate(self, input_mes):
       with torch.no_grad():
           tags_vals: list[str] = ['0', '1', '2']
           tkns = self.tokenizer.tokenize(input_mes)
           indexed_tokens = self.tokenizer.convert_tokens_to_ids(tkns)
           tokens_tensor = torch.tensor([indexed_tokens]).to("cuda")
           self.model.eval()
           try:
               logit = self.model(tokens_tensor).logits
           except Exception as e:
               print(f"Error during model execution: {str(e)}")
           predictions = torch.argmax(logit, dim=2)
           pred_tags = [tags_vals[p_i] for p_i in predictions[0]]
           original_tokens = self.tokenizer.convert_ids_to_tokens(indexed_tokens)
           merged_tokens = []
           keywords = []
           current_keyword = ""
           for orig_token, tag in zip(original_tokens, pred_tags):
               if orig_token.startswith("##"):
                   merged_tokens[-1] += orig_token[2:]
               else:
                   merged_tokens.append(orig_token)

           for token, tag in zip(merged_tokens, pred_tags):
               if tag == '0':
                   if current_keyword:
                       keywords.append(current_keyword)
                   current_keyword = token
               elif tag == '1':
                   current_keyword += " " + token
           if current_keyword:
               keywords.append(current_keyword)

           torch.cuda.empty_cache()

       return keywords

