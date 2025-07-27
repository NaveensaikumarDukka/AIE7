import arxiv
import os
import tempfile
from typing import List, Optional
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
import requests
from pathlib import Path

class ArxivFetcher:
    """
    A class to dynamically fetch and process Arxiv papers
    """
    
    def __init__(self, cache_dir: str = "./arxiv_cache"):
        """
        Initialize the ArxivFetcher
        
        Args:
            cache_dir: Directory to cache downloaded papers
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def search_papers(self, query: str, max_results: int = 5) -> List[dict]:
        """
        Search for papers on Arxiv based on a query
        
        Args:
            query: Search query for papers
            max_results: Maximum number of results to return
            
        Returns:
            List of paper metadata dictionaries
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in search.results():
            paper_info = {
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary,
                'pdf_url': result.pdf_url,
                'arxiv_id': result.entry_id.split('/')[-1],
                'published_date': result.published,
                'categories': result.categories
            }
            papers.append(paper_info)
        
        return papers
    
    def download_paper(self, pdf_url: str, arxiv_id: str) -> Optional[str]:
        """
        Download a paper PDF and save it to cache
        
        Args:
            pdf_url: URL of the PDF to download
            arxiv_id: Arxiv ID for the paper
            
        Returns:
            Path to the downloaded PDF file, or None if download failed
        """
        cache_file = self.cache_dir / f"{arxiv_id}.pdf"
        
        # Check if already cached
        if cache_file.exists():
            return str(cache_file)
        
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            return str(cache_file)
        except Exception as e:
            print(f"Failed to download paper {arxiv_id}: {e}")
            return None
    
    def fetch_and_process_papers(self, query: str, max_results: int = 3) -> List[Document]:
        """
        Search for papers, download them, and convert to LangChain Documents
        
        Args:
            query: Search query for papers
            max_results: Maximum number of papers to fetch
            
        Returns:
            List of LangChain Document objects
        """
        print(f"Searching Arxiv for papers about: {query}")
        
        # Search for papers
        papers = self.search_papers(query, max_results)
        
        if not papers:
            print("No papers found for the given query.")
            return []
        
        documents = []
        
        for paper in papers:
            print(f"Processing paper: {paper['title']}")
            
            # Download the paper
            pdf_path = self.download_paper(paper['pdf_url'], paper['arxiv_id'])
            
            if pdf_path:
                try:
                    # Load the PDF using PyMuPDFLoader
                    loader = PyMuPDFLoader(pdf_path)
                    docs = loader.load()
                    
                    # Add metadata about the paper
                    for doc in docs:
                        doc.metadata.update({
                            'source': 'arxiv',
                            'arxiv_id': paper['arxiv_id'],
                            'title': paper['title'],
                            'authors': paper['authors'],
                            'summary': paper['summary'],
                            'published_date': str(paper['published_date']),
                            'categories': paper['categories']
                        })
                    
                    documents.extend(docs)
                    print(f"Successfully processed paper: {paper['title']}")
                    
                except Exception as e:
                    print(f"Failed to process paper {paper['title']}: {e}")
            else:
                print(f"Failed to download paper: {paper['title']}")
        
        print(f"Successfully processed {len(documents)} document chunks from {len(papers)} papers")
        return documents
    
    def get_cached_papers(self) -> List[str]:
        """
        Get list of cached paper files
        
        Returns:
            List of cached PDF file paths
        """
        return [str(f) for f in self.cache_dir.glob("*.pdf")]
    
    def clear_cache(self):
        """
        Clear all cached papers
        """
        for file in self.cache_dir.glob("*.pdf"):
            file.unlink()
        print("Cache cleared")

# Example usage and testing
if __name__ == "__main__":
    fetcher = ArxivFetcher()
    
    # Test search
    papers = fetcher.search_papers("machine learning", max_results=2)
    print(f"Found {len(papers)} papers")
    
    # Test fetch and process
    docs = fetcher.fetch_and_process_papers("student loans", max_results=2)
    print(f"Processed {len(docs)} document chunks") 