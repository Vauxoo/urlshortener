# -*- coding: utf-8 -*-
# Copyright (c) 2016 by Ecreall under licence AGPL terms
# avalaible on http://www.gnu.org/licenses/agpl.html
# Source: https://github.com/narenaryan/Pyster
# licence: AGPL
# author: Amen Souissi
# hacked by: Nhomar Hernandez <nhomar@vauxoo.com>

import sqlite3
import string
import os
import click
from flask import Flask, request, render_template, redirect, jsonify
from flask import send_from_directory
from flask.ext.cors import CORS, cross_origin
from sqlite3 import OperationalError
from urllib.parse import urlparse


__version__ = '1.1.4'
db_path = 'var/urls.db'
host = os.environ.get("SHORTENER_DOMAIN", 'localhost:5000')
protocol = os.environ.get("PROTOCOL", 'http://')


BASE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
BASE.extend(list(string.ascii_lowercase))
BASE.extend(list(string.ascii_uppercase))
BASE_LEN = len(BASE)

# Assuming urls.db is in your app root folder
app = Flask(__name__)

cors = CORS(app, resources={r"/": {"origins": "*"}})


def get_base_next(char):
    if char == '':
        return False, '0'
    char_index = BASE.index(char)
    char_index += 1
    return (False, BASE[char_index]) if \
        char_index < BASE_LEN else (True, '0')


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
        while index + 6 >= 0 and final:
            if index + len_id >= 0:
                to_inc = new_id[index]
                final, next = get_base_next(to_inc)
                new_id = new_id[:index] + next + new_id[index + 1:]
            else:
                to_inc = ''
                final, next = get_base_next(to_inc)
                new_id = next + new_id[index + 1:]

            index -= 1

    return new_id


def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INTEGER PRIMARY KEY     AUTOINCREMENT,
        NUM TEXT NOT NULL UNIQUE,
        URL  TEXT  NOT NULL UNIQUE
        );
        """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def home():
    method = request.method
    with sqlite3.connect(db_path) as conn:
        try:
            cursor = conn.cursor()
            rows_query = """
                SELECT NUM, max(ID) FROM WEB_URL"""
            result_cursor = cursor.execute(rows_query)
            result_fetch = result_cursor.fetchone()
            last_num = result_fetch[0]
            number_of_rows = result_fetch[1]
            number_of_rows = 0 if number_of_rows is None else number_of_rows
            if (method == 'GET' and request.args.get('url', None)) or \
               method == 'POST':
                original_url = request.args.get('url') if \
                    method == 'GET' else request.form.get('url')
                if original_url:
                    if urlparse(original_url).scheme == '':
                        original_url = 'http://' + original_url
                    exist_row = """
                        SELECT NUM FROM WEB_URL
                            WHERE URL='{url}'
                        """.format(url=original_url)
                    result_cursor = cursor.execute(exist_row)
                    result_fetch = result_cursor.fetchone()
                    if result_fetch:
                        new_num = result_fetch[0]
                    else:
                        new_num = next_id(last_num)
                        insert_row = """
                            INSERT INTO WEB_URL (URL, NUM)
                                VALUES ('{url}', '{num}')
                            """.format(url=original_url, num=new_num)
                        cursor.execute(insert_row)
                        number_of_rows += 1
                    encoded_string = new_num
                    short_url = '/'.join([host, encoded_string])
                    if method == 'GET':
                        return jsonify({'short_url': short_url,
                                        'code': 'SUCCESS',
                                        'original_url': original_url,
                                        'version': __version__})
                    else:
                        return render_template(
                            'home.html', short_url=short_url,
                            protocol=protocol,
                            number_of_rows=number_of_rows,
                            version=__version__)

            return render_template('home.html',
                                   protocol=protocol,
                                   number_of_rows=number_of_rows,
                                   version=__version__)
        except Exception as error:
            if method == 'GET':
                return jsonify(**{'code': 'ERROR',
                                  'error': str(error),
                                  'original_url': original_url
                                  })
            else:
                return render_template(
                    'home.html',
                    number_of_rows=number_of_rows,
                    error=True)


@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded_string = short_url
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        select_row = """
                SELECT URL FROM WEB_URL
                    WHERE NUM='{num}'
                """.format(num=decoded_string)
        result_cursor = cursor.execute(select_row)
        try:
            return redirect(result_cursor.fetchone()[0])
        except Exception:
            pass

    return render_template(
        'home.html',
        error=True)


@click.option('--version', help='Print Version and exit',
              is_flag=True)
@click.option('--debug', help='Enable debug option',
              is_flag=True)
@click.command()
def main(debug, version):
    if version:
        import sys
        sys.exit('Your Version is: %s' % __version__)
    table_check()
    app.run(host='0.0.0.0', debug=debug)


if __name__ == '__main__':
    main()
