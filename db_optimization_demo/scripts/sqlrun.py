#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mysql CLI 替代包装器：执行 SQL 并以表格形式打印结果"""
import sys, pymysql

def run_sql(sql, db='shop_demo'):
    conn = pymysql.connect(host='localhost', user='root', password='root123',
                           database=db, charset='utf8mb4',
                           unix_socket='/var/run/mysqld/mysqld.sock')
    try:
        with conn.cursor() as cur:
            for stmt in [s.strip() for s in sql.split(';') if s.strip()]:
                cur.execute(stmt)
                if cur.description:
                    cols = [d[0] for d in cur.description]
                    rows = cur.fetchall()
                    # 简易表格输出
                    widths = [max(len(str(c)), *(len(str(r[i])) for r in rows)) for i, c in enumerate(cols)]
                    print('+' + '+'.join('-'*(w+2) for w in widths) + '+')
                    print('| ' + ' | '.join(str(c).ljust(w) for c, w in zip(cols, widths)) + ' |')
                    print('+' + '+'.join('-'*(w+2) for w in widths) + '+')
                    for r in rows:
                        print('| ' + ' | '.join(str(v).ljust(w) for v, w in zip(r, widths)) + ' |')
                    print('+' + '+'.join('-'*(w+2) for w in widths) + '+')
                else:
                    print(f"  → affected {cur.rowcount} rows")
    finally:
        conn.close()

if __name__ == '__main__':
    sql = sys.stdin.read()
    run_sql(sql)
