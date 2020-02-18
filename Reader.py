import json
import jieba.analyse

if __name__ == '__main__':
    with open('sample.json') as json_file:
        datas = json.load(json_file)
        for data in datas:
            keywords = []
            try:
                data['poem'] = "haha"
                image = data['image']
                # print(data)
                print(data)
                print(data['result'])
                for result in data['result']:
                    keyword = result['keyword']
                    score = result['score']
                    # throw away the keyword with confidence score less than threshold --> 0.1
                    # could change it during the following experiment
                    if score > 0.1:
                        tf_idf_res = jieba.cut_for_search(keyword)
                        keywords += tf_idf_res
                    else:
                        continue
                keyword_to_search = "@".join(keywords)
                print(keyword_to_search)
            except:
                continue
