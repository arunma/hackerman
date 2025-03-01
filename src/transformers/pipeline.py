import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable
from tqdm import tqdm
from dotenv import load_dotenv

from .base import Transformer

class TransformerPipeline:
    def __init__(self, transformers: List[Transformer]):
        self.transformers = transformers
        load_dotenv()
        self.max_workers = int(os.getenv('MAX_WORKER_THREADS', '4'))

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all transformations in sequence"""
        result = data
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result

    def process(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single item through all transformers in sequence"""
        for transformer in self.transformers:
            item = transformer.transform(item)
        return item

    def process_parallel(self, items: List[Dict[str, Any]], post_process_fn: Callable = None) -> List[Dict[str, Any]]:
        """Process multiple items in parallel with progress bar"""
        results = []
        total_items = len(items)

        def process_item(item: Dict[str, Any]) -> Dict[str, Any]:
            """Process a single item through the pipeline"""
            result = self.transform(item)
            if post_process_fn:
                result = post_process_fn(result)
            return result

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(process_item, item): item 
                for item in items
            }
            
            # Process completed tasks with progress bar
            with tqdm(total=total_items, desc="Processing items") as pbar:
                for future in as_completed(future_to_item):
                    item = future_to_item[future]
                    try:
                        result = future.result()
                        results.append(result)
                        pbar.set_postfix_str(f"Processed: {result.get('title', '')[:30]}...")
                    except Exception as e:
                        print(f"Error processing item {item.get('title', 'Unknown')}: {str(e)}")
                    finally:
                        pbar.update(1)

        return results
