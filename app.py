from flask import Flask, render_template, request, session, json
import flask
import logging
import museumbot.bot as bot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcd'
app.config['SESSION_TYPE'] = 'filesystem'

logger = logging.getLogger('QApair')

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# log 출력
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# log를 파일에 출력
file_handler = logging.FileHandler('./Logs/chatbot_logging.txt')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

present_order = {
    "G1": ['A', 'B', 'D', 'C'],
    "G2": ['B', 'C', 'A', 'D'],
    "G3": ['C', 'D', 'B', 'A'],
    "G4": ['D', 'A', 'C', 'B']
    # "E1": ['A', 'B', 'D', 'C'],
    # "E2": ['B', 'C', 'A', 'D'],
    # "E3": ['C', 'D', 'B', 'A'],
    # "E4": ['D', 'A', 'C', 'B']
}

graph_url = {
    "1": "https://www.mindmeister.com/maps/public_map_shell/1979179677/_?width=600&height=400&z=auto",
    "2": "https://www.mindmeister.com/maps/public_map_shell/1979199233/_?width=600&height=400&z=auto",
    "3": "https://www.mindmeister.com/maps/public_map_shell/1979255443/_?width=600&height=400&z=auto",
    "4": "https://www.mindmeister.com/maps/public_map_shell/1979255918/_?width=600&height=400&z=auto",
    # "1": "https://www.mindmeister.com/maps/public_map_shell/1979179677/_?width=600&height=400&z=auto",
    # "2": "https://www.mindmeister.com/maps/public_map_shell/1979199233/_?width=600&height=400&z=auto",
    # "3": "https://www.mindmeister.com/maps/public_map_shell/1979255443/_?width=600&height=400&z=auto",
    # "4": "https://www.mindmeister.com/maps/public_map_shell/1979255918/_?width=600&height=400&z=auto"

}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        group = request.form['groupname']
        # password = request.form['password']
        try:
            if name != "" and group != "":
                session["logged_in"] = True
                session["user_id"] = name
                session["group"] = group
                session["order"] = present_order[session["group"]]  # current stage (1 ~ 4)
                session["stage"] = 1
                session["final_entity"] = []
                session["final_intent"] = []

                result = make_json(1)
                first_html = 'type' + session['order'][0] + '.html'
                return result
                # return render_template(first_html, first_load=result)
            else:
                return '모든 정보를 입력한 후 다시 시도하세요.'
        except:
            return 'Dont login'
    else:
        return render_template('login.html')

@app.route('/typeA.html')
def get_typeA():
    return render_template('typeA.html')

@app.route('/typeB.html')
def get_typeB():
    my_res = flask.Response()
    my_res.headers['Access-Control-Allow-Origin'] = "*"
    return render_template('typeB.html')

@app.route('/typeC.html')
def get_typeC():
    return render_template('typeC.html')

@app.route('/typeD.html', methods=['POST', 'GET'])
def task1_function():
    
    answer = "죄송해요. 제가 드릴 수 있는 답변이 없네요. T.T"  # default answer
    return render_template('typeD.html', bot_answer=answer)


alt_list = [
    '이 유물', '이유물', '저 유물', '저유물', '이것', '그것', '이 것', '그 것',
    '이 도자기', '저 도자기'
]

# @app.route('/get_answer', methods=['POST', 'GET'])
# def get_answer():
#     if request.method == 'POST':
#         question = request.form['question_id']
#         title = request.form['title']
#         title = title.rstrip('\n')
#         # print(question, title)

#         for alt in alt_list:
#             # print(alt, question)
#             if alt in question:
#                 question = question.replace(alt, title)

#         # print(question)
#         res, answer, session['final_entity'], session['final_intent'] = bot.search_answer_from_bot(question, session[
#             'final_entity'], session['final_intent'])

#         logger.info(f'%s,%s,%s,%s,%s,%s,%s' % (session["user_id"], title, question, res, answer, session['final_entity'], session['final_intent']))

#         return answer

@app.route('/get_answer', methods=['POST', 'GET'])
def get_answer():
    if request.method == 'POST':
        question = request.form['question_id']
        title = request.form['title']
        title = title.rstrip('\n')
        # print(question, title)

        for alt in alt_list:
            # print(alt, question)
            if alt in question:
                question = question.replace(alt, title)

        # print(question)
        res, answer, imgs, session['final_entity'], session['final_intent'] = bot.search_answer_from_bot(question, session[
            'final_entity'], session['final_intent'])

        logger.info(f'%s,%s,%s,%s,%s,%s,%s' % (session["user_id"], title, question, res, answer, session['final_entity'], session['final_intent']))

        result = json.dumps({
            'answer': answer,
            'imgs': imgs
        })

        return result


# @app.route('/en/typeA.html')
# def get_typeA_en():
#     return render_template('typeA_en.html')
#
# @app.route('/en/typeB.html')
# def get_typeB_en():
#     return render_template('typeB_en.html')
#
# @app.route('/en/typeC.html')
# def get_typeC_en():
#     return render_template('typeC_en.html')
#
# @app.route('/en/typeD.html')
# def get_typeD_en():
#     return render_template('typeD_en.html')


@app.route('/next_paging', methods=['POST', 'GET'])
def next_paging():
    if request.method == 'POST':
        paging = request.form['paging']
        now_page, total_page = paging.split('/')
        next_page = int(now_page) +1

        session['stage'] = next_page
        content = search_database(next_page)

        result = make_json(next_page)

        return result

@app.route('/prev_paging', methods=['POST', 'GET'])
def prev_paging():
    if request.method == 'POST':
        paging = request.form['paging']
        now_page, total_page = paging.split('/')
        prev_page = int(now_page) - 1

        session['stage'] = prev_page

        result = make_json(prev_page)

        return result

def make_json(pagenum):
    content = search_database(pagenum)

    result = json.dumps({
        'target_html': 'type' + session['order'][pagenum - 1] + '.html',
        'title': content["title"],
        # 'title': '검은점무늬 항아리',
        'text-area': content["description"],
        'li': content["li"],
        'img_url': "http://127.0.0.1:5000/static/image/%s.jpg" % pagenum,
        'video': "http://127.0.0.1:5000/static/video/video.mp4",
        'dynamic_html': "http://127.0.0.1:5000/static/description_html/%s_typeB.html" % pagenum,
        # 'dynamic_html': "http://127.0.0.1:5000/static/description_html/%s_typeB_en.html" % pagenum,        # FOR ENGLISH DEMO
        "graph_url": graph_url[str(pagenum)]
    })

    return result

def search_database(page_num):
    with open('static/description/%s.txt' % str(page_num), 'r', encoding='UTF8') as f:
    # with open('static/description/%s_en.txt' % str(page_num), 'r', encoding='UTF8') as f:  # FOR ENGLISH DEMO
        content = f.readlines()
        title = content[0]

        li = []
        description = []
        for line in content[1:]:
            if "-" in line:
                line.replace("-", "")
                li.append(line)
            else:
                # otherwise, description
                description.append(line)

        description = "".join(description)

        return {"title": title, "li": li, "description": description}


if __name__ == '__main__':
    app.run(debug=True)