# Copyright (c) 2016 by Ecreall under licence AGPL terms
# avalaible on http://www.gnu.org/licenses/agpl.html
#Source: https://github.com/narenaryan/Pyster
# licence: AGPL
# author: Amen Souissi

import sqlite3
import base64
import string
from flask import Flask, request, render_template, redirect, jsonify
from sqlite3 import OperationalError
from urlparse import urlparse

host = 'http://localhost:5000/'

BASE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
BASE.extend(list(string.ascii_lowercase))
BASE.extend(list(string.ascii_uppercase))
BASE_LEN = len(BASE)

#Assuming urls.db is in your app root folder
app = Flask(__name__)


def get_base_next(char):
    if char == '':
        return False, '0'

    char_index = BASE.index(char)
    char_index += 1
    if char_index < BASE_LEN:
        return False, BASE[char_index]
    else:
        return True, '0'


def next_id(id_=None):
    new_id = id_
    if id_ is None:
        new_id = '0'
    else:
        index = -1
        to_inc = new_id[index]
        final, next = get_base_next(to_inc)
        new_id = new_id[:index] + next
        index -= 1
        len_id = len(new_id)
        while index+6 >= 0 and final:
            if index+len_id >= 0:
                to_inc = new_id[index]
                final, next = get_base_next(to_inc)
                new_id = new_id[:index] + next + new_id[index+1:]
            else:
                to_inc = ''
                final, next = get_base_next(to_inc)
                new_id = next + new_id[index+1:]

            index -= 1

    return new_id


def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INTEGER PRIMARY KEY     AUTOINCREMENT,
        NUM TEXT NOT NULL,
        URL  TEXT  NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


@app.route('/', methods=['GET', 'POST'])
def home():
    method = request.method
    if method in ('GET', 'POST'):
        original_url = request.args.get('url') if \
            method == 'GET' else request.form.get('url')
        if urlparse(original_url).scheme == '':
            original_url = 'http://' + original_url
        with sqlite3.connect('urls.db') as conn:
            try:
                cursor = conn.cursor()
                last_curso = """
                    SELECT NUM, max(ID) FROM WEB_URL
                    """
                result_id = cursor.execute(last_curso)
                result_id = result_id.fetchone()[0]
                new_id = next_id(result_id)
                insert_row = """
                    INSERT INTO WEB_URL (URL, NUM)
                        VALUES ('{url}', '{id}')
                    """.format(url=original_url, id=new_id)
                cursor.execute(insert_row)
                encoded_string = base64.urlsafe_b64encode(new_id)
                if method == 'GET':
                    return jsonify(**{'short_url': host + encoded_string})
                else:
                    return render_template(
                        'home.html', short_url=host + encoded_string)

            except Exception as e:
                print e

    return render_template('home.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded_string = base64.urlsafe_b64decode(short_url.encode())
    redirect_url = host
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        select_row = """
                SELECT URL FROM WEB_URL
                    WHERE NUM='{num}'
                """.format(num=decoded_string)
        result_cursor = cursor.execute(select_row)
        try:
            redirect_url = result_cursor.fetchone()[0]
        except Exception as e:
            print e
    return redirect(redirect_url)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    app.run(debug=True)
