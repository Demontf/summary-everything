from fetch_paper import fetch_papers_from_arxiv_advanced

if __name__ == '__main__':
    papers = fetch_papers_from_arxiv_advanced()
    total = len(papers)
    if total == 0:
        print("today no more paper")
    else:
        print("send email")
        # todo send func in outlook
