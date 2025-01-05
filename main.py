from fetch_paper import fetch_papers_from_arxiv_advanced
from model_factory import ModelFactory

if __name__ == '__main__':
    papers = fetch_papers_from_arxiv_advanced()
    total = len(papers)
    
    if total == 0:
        print("No new papers found today")
    else:
        print(f"Found {total} papers, starting summary process...")
        summaries = ModelFactory.summary_papers(papers)
        print(f"Successfully summarized {len(summaries)} papers")
        print("Sending email...")
        # todo send func in outlook
