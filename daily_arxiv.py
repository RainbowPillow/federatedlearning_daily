import datetime
import requests
import json
import arxiv
import os

base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"


def get_authors(authors, first_author=False):
    output = str()
    if first_author == False:
        output = ", ".join(str(author) for author in authors)
    else:
        output = authors[0]
    return output


def sort_papers(papers):
    output = dict()
    keys = list(papers.keys())
    keys.sort(reverse=True)
    for key in keys:
        output[key] = papers[key]
    return output


def get_daily_papers(topic, query="slam", max_results=2):
    """
    @param topic: str
    @param query: str
    @return paper_with_code: dict
    """

    # output
    content = dict()
    content_to_web = dict()

    # content
    output = dict()

    search_engine = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    cnt = 0

    for result in search_engine.results():

        paper_id = result.get_short_id()
        paper_title = result.title
        paper_url = result.entry_id

        # None if not existed
        comment = '~'
        if result.comment:
            comment = result.comment.replace(
                '\r', '').replace('\n', '').replace('\t', '')

        code_url = base_url + paper_id
        paper_abstract = result.summary.replace("\n", " ")
        paper_authors = get_authors(result.authors)
        paper_first_author = get_authors(result.authors, first_author=True)
        primary_category = result.primary_category

        publish_time = result.published.date()

        print("Time = ", publish_time,
              " title = ", paper_title,
              ' comment = ', comment)

        # eg: 2108.09112v1 -> 2108.09112
        ver_pos = paper_id.find('v')
        if ver_pos == -1:
            paper_key = paper_id
        else:
            paper_key = paper_id[0:ver_pos]

        try:
            r = requests.get(code_url).json()
            # source code link
            if "official" in r and r["official"]:
                cnt += 1
                repo_url = r["official"]["url"]
                content[paper_key] = f"|**{publish_time}**|**[{paper_title}]({paper_url})**|{comment}|[code]({repo_url})|\n"
                # content_to_web[
                #     paper_key] = f"|**{publish_time}**, **[{paper_title}]({paper_url})**,**{comment}**,**[code]({repo_url})**\n"
            else:
                content[paper_key] = f"|**{publish_time}**|**[{paper_title}]({paper_url})**|{comment}|~|\n"
                # content_to_web[
                #     paper_key] = f"|**{publish_time}**, **[{paper_title}]({paper_url})**,**{comment}**,~\n"

        except Exception as e:
            print(f"exception: {e} with id: {paper_key}")

    # data = {topic: content}
    # data_web = {topic: content_to_web}
    # return content, content_to_web
    return content


def update_json_file(filename, content, topic):
    
    if not os.path.exists(filename):
        with open(filename, "w+") as f:
            if init == True:
                f.write('')

    with open(filename, "r") as f:
        temp = f.read()
        if not temp:
            json_data = {}
        else:
            json_data = json.loads(temp)

    # json_data = m.copy()

    if topic in json_data.keys():
        json_data[topic].update(content)
    else:
        json_data[topic] = content

    with open(filename, "w") as f:
        json.dump(json_data, f)


def json_to_md(topic, filename, to_web=False):
    """
    @param filename: str
    @return None
    """

    md_path = './md/'
    web_md_path = './docs/md/'

    DateNow = datetime.date.today()
    DateNow = str(DateNow)
    DateNow = DateNow.replace('-', '.')

    with open(filename, "r") as f:
        content = f.read()
        if not content:
            data = {}
        else:
            data = json.loads(content)

    if to_web == False:
        # md_filename = "README.md"
        md_filename = md_path+topic+'.md'
    else:
        md_filename = web_md_path+topic+'.md'

    # clean README.md if daily already exist else create it
    with open(md_filename,"w+") as f:
        pass

    # clean README.md if daily already exist else create it
    with open(md_filename, "a+") as f:
        if to_web == True:
            f.write("---\n" + "layout: default\n" + "---\n\n")

        if to_web:
            f.write("[main page](../index.md)\n\n")
        else:
            f.write("[main page](../readme.md)\n\n")
        
        for keyword in data.keys():
            day_content = data[keyword]
            if not day_content:
                continue
            # the head of each part
            f.write(f"# {keyword.upper()}\n\n")

            # f.write("|Date|Title|Comment|Code|\n" + "|---|---|---|---|\n")
            if to_web == False:
                f.write("|Date|Title|Comment|Code|\n")
                f.write("|----|-----|-------|----|\n")
            else:
                f.write("| Date | Title | Comment | Code |\n")
                f.write("|:-----|:------|:--------|:-----|\n")

            # sort papers by date
            day_content = sort_papers(day_content)

            for _, v in day_content.items():
                if v is not None:
                    f.write(v)

            f.write(f"\n")
        # pass

    # write data into README.md
    # with open(md_filename, "a+") as f:

    #     if to_web == True:
    #         f.write("---\n" + "layout: default\n" + "---\n\n")

    #     # f.write("## Updated on " + DateNow + "\n\n")

    #     for keyword in data.keys():
    #         day_content = data[keyword]
    #         if not day_content:
    #             continue
    #         # the head of each part
    #         f.write(f"## {keyword.upper()}\n\n")

    #         if to_web == False:
    #             f.write("|Date|Title|Comment|Code|\n" + "|---|---|---|---|\n")
    #         else:
    #             f.write("| Date | Title | Comment | Code |\n")
    #             f.write("|:---------|:-----------------------|:---------|:---------|\n")

    #         # sort papers by date
    #         day_content = sort_papers(day_content)

    #         for _, v in day_content.items():
    #             if v is not None:
    #                 f.write(v)

    #         f.write(f"\n")


if __name__ == "__main__":

    web_json_path = './docs/json/'
    json_path = './json/'
    init = False
    demo = False
    num_result = 500
    if init:
        num_result = 50
    if demo:
        num_result = 2
    data_collector = []
    data_collector_web = []

    keywords = {
        'fl': "abs:federated\ learning",
        'tsc': "abs:time\ series",
        'ad': "abs:anomaly\ detection"
    }

    for topic, keyword in keywords.items():

        # topic = keyword.replace("\"","")
        print("Keyword: " + topic)

        content = get_daily_papers(
            topic, query=keyword, max_results=num_result)

        json_file = json_path + topic + "-arxiv-daily.json"
        update_json_file(json_file, content, topic)
        json_to_md(topic, json_file)

        json_web_file = web_json_path + topic+"-arxiv-daily-web.json"
        update_json_file(json_web_file, content, topic)
        json_to_md(topic, json_web_file, to_web=True)
    print('finished')
