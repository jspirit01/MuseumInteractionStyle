from flask import Flask, render_template, request, session, json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcd'

app.config['SESSION_TYPE'] = 'filesystem'

present_order = {
    "G1": ['A', 'B', 'D', 'C'],
    "G2": ['B', 'C', 'A', 'D'],
    "G3": ['C', 'D', 'B', 'A'],
    "G4": ['D', 'A', 'C', 'B']
}

graph_url = {
    "1": "https://www.mindmeister.com/maps/public_map_shell/1979179677/_?width=600&height=400&z=auto",
    "2": "https://www.mindmeister.com/maps/public_map_shell/1979199233/_?width=600&height=400&z=auto",
    "3": "https://www.mindmeister.com/maps/public_map_shell/1979255443/_?width=600&height=400&z=auto",
    "4": "https://www.mindmeister.com/maps/public_map_shell/1979255918/_?width=600&height=400&z=auto"
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
    return render_template('typeB.html')


@app.route('/typeC.html')
def get_typeC():
    return render_template('typeC.html')

@app.route('/typeD.html')
def get_typeD():
    return render_template('typeD.html')


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
        # 'img_url': "http://127.0.0.1:5000/static/image/sample.jpg",
        'video': "http://127.0.0.1:5000/static/video/video.mp4",
        'dynamic_html': "http://127.0.0.1:5000/static/description_html/%s_typeB.html" % pagenum,
        # 'dynamic_html': "http://127.0.0.1:5000/static/description_html/sample.html"
        "graph_url": graph_url[str(pagenum)]
    })

    return result

def search_database(page_num):
    with open('static/description/%s.txt' % str(page_num), 'r', encoding='UTF8') as f:
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