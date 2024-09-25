from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

from qwen import summary_papers
from tools import get_date_x_days_ago, save_obj_json
import requests, re
from datetime import datetime

max_paper_size = 200
paper_classification_term = 'cs.AI'


def fetch_papers_from_arxiv_advanced():
    # arxiv提供最新的论文 为 today - 3
    from_date = get_date_x_days_ago(3)
    end_date = get_date_x_days_ago(2)

    url = "https://arxiv.org/search/advanced?advanced=1&" \
          "terms-0-operator=AND&terms-0-term=" + paper_classification_term + "&terms-0-field=all&" \
                                                                             "classification-computer_science=y&classification-physics_archives=all&" \
                                                                             "classification-include_cross_list=include&date-year=&date-filter_by=date_range&" \
                                                                             "date-from_date=" + from_date + "&date-to_date=" + end_date + "&date-date_type=submitted_date&" \
                                                                                                                                           "abstracts=show&size=" + str(
        max_paper_size) + "&order=-announced_date_first"

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(url, verify=False)

    if response.status_code != 200:
        print(f"arxiv access error {response.status_code}")
        print(response.content)
        return []

    print(f"fetch {max_paper_size} paper from arxiv success")
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    # find all papers
    papers = soup.find_all("li", class_="arxiv-result")

    papers_info = {}
    paper_for_qwen = []

    for paper in papers:
        title = paper.find("p", class_="title is-5 mathjax").get_text(strip=True)
        abstract = paper.find("span", class_="abstract-full").get_text(strip=True)[0:-6]  # cut ^less
        authors = paper.find("p", class_="authors").get_text(strip=True).replace("Authors:", "").strip()
        submitted = paper.find("p", class_="is-size-7").get_text(strip=True).split(';')[0].replace('Submitted',
                                                                                                   '').strip()
        arxiv_id = re.search(r'arXiv:(\d+\.\d+)',
                             paper.find("p", class_="list-title is-inline-block").get_text(strip=True)).group(1)

        papers_info[arxiv_id] = {
            "title": title,
            "summary": abstract,
            "authors": authors,
            "time": submitted,
            "pdf_url": "https://arxiv.org/pdf/" + arxiv_id,
            "id": arxiv_id
        }
        paper_for_qwen.append({
            "title": title,
            "summary": abstract,
            "id": arxiv_id,
        })

    save_obj_json("./log/" + datetime.now().strftime("%Y-%m-%d") + "/papers_info_without_one.json", papers_info)
    print("parse paper info success, data for qwen is saved")

    if len(paper_for_qwen) != 0:
        print("start to summary paper by Qwen LLM")
        ret_summary_list = summary_papers(paper_for_qwen)
        for summary_group in ret_summary_list:
            for item in summary_group:
                papers_info[item["id"]]['one'] = item['one']

    save_obj_json("./log/" + datetime.now().strftime("%Y-%m-%d") + "/papers_info.json", papers_info)
    return papers_info
