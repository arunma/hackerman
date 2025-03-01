import os
import argparse
from dotenv import load_dotenv
from elasticsearch_dsl.connections import connections
from tqdm import tqdm

from transformers.pipeline import TransformerPipeline
from repository import Article
from config import Config

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Hackerman: Hacker News Content Pipeline')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to YAML configuration file')
    args = parser.parse_args()

    # Load configuration
    source, transformers, formatter, destination = Config.from_yaml(args.config)
    
    # Get elasticsearch host from environment
    load_dotenv()
    es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost:9200')
    
    # Connect to Elasticsearch
    connections.create_connection(hosts=[es_host])
    
    # Initialize pipeline
    pipeline = TransformerPipeline(transformers)
    
    # Fetch stories
    stories = source.fetch_data()
    
    # Process stories through the pipeline
    processed_stories = []
    with tqdm(total=len(stories), desc="Processing stories") as pbar:
        for story in stories:
            processed_story = pipeline.process(story)
            processed_stories.append(processed_story)
            pbar.update(1)
    
    # Format all stories at once
    formatted_content = formatter.format("", processed_stories)
    
    # Process and send stories to Elasticsearch and destination
    def process_and_send(data: dict) -> dict:
        # Save to Elasticsearch
        article = Article.from_dict(data)
        article.save()
        
        # Send to destination
        destination.send(formatted_content, metadata=data)
        
        return data

    # Process all stories
    for story in processed_stories:
        process_and_send(story)

if __name__ == "__main__":
    main()
