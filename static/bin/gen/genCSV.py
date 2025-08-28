import csv
import os

from flask import send_file, make_response
from datetime import datetime

def gen_csv(data, header, filename):

    os.makedirs(os.path.join(os.getcwd(), 'tmp'), exist_ok=True)
    csv_path = os.path.join(os.getcwd(), 'tmp', filename)



    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in data:
            row = list(row)  # Convertit le tuple en liste
            row[0] = datetime.fromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(row)

    response = make_response(send_file(csv_path, mimetype='text/csv'))
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response