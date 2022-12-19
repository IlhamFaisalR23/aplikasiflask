from distutils.log import debug
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash,send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'aplikasiflask'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
@app.route('/aplikasi/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'namapengguna' in request.form and 'katasandi' in request.form:
        namapengguna = request.form['namapengguna']
        katasandi = request.form['katasandi']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM akun WHERE namapengguna = %s AND katasandi = %s', (namapengguna, katasandi,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['namapengguna'] = account['namapengguna']
            return redirect(url_for('home'))
        else:
            msg = 'Nama Pengguna atau Kata Sandi Salah!'
    return render_template('index.html', msg=msg)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/aplikasi/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('namapengguna', None)
   return redirect(url_for('login'))

@app.route('/aplikasi/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'nip' in request.form and 'namapengguna' in request.form and 'katasandi' in request.form and 'status' in request.form:
        nip = request.form['nip']
        namapengguna = request.form['namapengguna']
        katasandi = request.form['katasandi']
        status = request.form['status']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM akun WHERE namapengguna = %s', (namapengguna,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', namapengguna):
            msg = 'Username must contain only characters and numbers!'
        elif not nip or not namapengguna or not katasandi:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO akun VALUES (NULL, %s, %s, %s, %s)', (nip, namapengguna, katasandi, status,))
            mysql.connection.commit()
            msg = 'Anda telah register!'
            

            
    elif request.method == 'POST':
        msg = 'Tolong isi form'
    return render_template('register.html', msg=msg)

@app.route('/aplikasi/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', namapengguna=session['namapengguna'])
    return redirect(url_for('login'))

@app.route('/aplikasi/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM akun WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/aplikasi/lihat')
def lihat():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM kartuindonesiamaju INNER JOIN statusfasilitas ON statusfasilitas.id_fasilitas = kartuindonesiamaju.id_fasilitas')
    data = cur.fetchall()
    cur.close()
    return render_template('lihat.html', anggota=data)

@app.route('/aplikasi/order')
def order():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM kartuindonesiamaju INNER JOIN statusfasilitas ON statusfasilitas.id_fasilitas = kartuindonesiamaju.id_fasilitas')
    data = cur.fetchall()
    cur.close()
    return render_template('order.html', anggota=data)

@app.route('/aplikasi/order/pesan/<int:id>', methods=['GET', 'POST'])
def orderorang(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM kartuindonesiamaju INNER JOIN statusfasilitas ON statusfasilitas.id_fasilitas = kartuindonesiamaju.id_fasilitas
        WHERE nomorkartu=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('pesan.html', row=row)
    else:
        nomorkartu = request.form['nomorkartu']
        nama = request.form['nama']
        alamat = request.form['alamat']
        lahir = request.form['lahir']
        nik = request.form['nik']
        id_fasilitas = request.form['id_fasilitas']
        jumlahorder = request.form['jumlahorder']

        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO pemesanan(nomorkartu, nama, alamat, lahir, nik, id_fasilitas, jumlahorder, tanggalorder) VALUES(%s,%s,%s,%s,%s,%s,%s,NOW())''',(nomorkartu, nama, alamat, lahir, nik, id_fasilitas, jumlahorder))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('order'))


@app.route('/aplikasi/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'GET':
        return render_template('tambah.html')
    else:
        nomorkartu = request.form['nomorkartu']
        nama = request.form['nama']
        alamat = request.form['alamat']
        lahir = request.form['lahir']
        nik = request.form['nik']
        id_fasilitas = request.form['id_fasilitas']

        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO kartuindonesiamaju(nomorkartu, nama, alamat, lahir, nik, id_fasilitas) VALUES(%s,%s,%s,%s,%s,%s)''',(nomorkartu, nama, alamat, lahir, nik, id_fasilitas))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('lihat'))

@app.route('/aplikasi/lihat/edit/<int:id>', methods=['GET', 'POST'])
def editanggota(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM kartuindonesiamaju INNER JOIN statusfasilitas ON statusfasilitas.id_fasilitas = kartuindonesiamaju.id_fasilitas
        WHERE nomorkartu=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('edit.html', row=row)
    else:
        nomorkartu = request.form['nomorkartu']
        nama = request.form['nama']
        alamat = request.form['alamat']
        lahir = request.form['lahir']
        nik = request.form['nik']
        id_fasilitas = request.form['id_fasilitas']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE kartuindonesiamaju 
        SET 
            nomorkartu = %s,
            nama = %s,
            alamat = %s,
            lahir = %s,
            nik = %s,
            id_fasilitas = %s
        WHERE
            idanggota = %s;
        ''',(nomorkartu,nama,alamat,lahir,nik,id_fasilitas,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('lihat'))

@app.route('/aplikasi/lihat/detail/<int:id>', methods=['GET', 'POST'])
def detailanggota(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM kartuindonesiamaju 
        WHERE nomorkartu=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('detail.html', row=row)

@app.route('/aplikasi/lihat/delete/<int:id>', methods=['GET'])
def deleteanggota(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE 
        FROM kartuindonesiamaju 
        WHERE nomorkartu=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('lihat'))

    return render_template('lihat.html')

if __name__ == '__main__':
    app.run(port=5000 ,debug=True)
    