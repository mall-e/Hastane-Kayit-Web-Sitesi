import datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import Randevu, TibbiRapor, db, User, Hasta, Doktor, Yonetici
from forms import LoginForm
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:efmukl123@localhost/saglik'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        app.logger.info(f"Login attempt for username: {form.username.data}")
        user = User.query.filter_by(username=form.username.data).first()
        app.logger.info(f"Query result: {user}")
        if user:
            app.logger.info(f"Found user: {user.username}")
            app.logger.info(f"Password in DB: {user.password}, Password entered: {form.password.data}")
            if user.password == form.password.data:
                login_user(user)
                flash('Giriş başarılı!', 'success')
                if user.role == 'hasta':
                    return redirect(url_for('hasta_home'))
                elif user.role == 'doktor':
                    return redirect(url_for('doktor_home'))
                elif user.role == 'yonetici':
                    return redirect(url_for('yonetici_home'))
            else:
                flash('Şifre yanlış.', 'danger')
                app.logger.info(f"Incorrect password for user: {user.username}")
        else:
            flash('Kullanıcı adı bulunamadı.', 'danger')
            app.logger.info(f"User not found: {form.username.data}")
    return render_template('login.html', form=form)

@app.route('/hasta_home')
@login_required
def hasta_home():
    if current_user.role != 'hasta':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))
    randevular = Randevu.query.filter_by(hasta_id=current_user.id).all()
    tibbi_raporlar = TibbiRapor.query.filter_by(hasta_id=current_user.id).all()
    return render_template('hasta_home.html', randevular=randevular, tibbi_raporlar=tibbi_raporlar)

@app.route('/doktor_home')
@login_required
def doktor_home():
    if current_user.role != 'doktor':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    doktor = Doktor.query.filter_by(username=current_user.username).first()
    if not doktor:
        flash('Doktor kaydı bulunamadı.', 'danger')
        return redirect(url_for('index'))

    doktor_id = doktor.id
    app.logger.info(f"Doktor ID: {doktor_id}")

    randevular = Randevu.query.filter_by(doktor_id=doktor_id).all()
    app.logger.info(f"Randevular: {randevular}")

    return render_template('doktor_home.html', randevular=randevular)

@app.route('/yonetici_home')
@login_required
def yonetici_home():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    hastalar = Hasta.query.all()
    doktorlar = Doktor.query.all()
    return render_template('yonetici_home.html', hastalar=hastalar, doktorlar=doktorlar)

@app.route('/admin/hastalar', methods=['GET', 'POST'])
@login_required
def admin_hastalar():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    hastalar = Hasta.query.all()
    return render_template('admin_hastalar.html', hastalar=hastalar)

@app.route('/admin/hasta_ekle', methods=['GET', 'POST'])
@login_required
def admin_hasta_ekle():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        ad = request.form['ad']
        soyad = request.form['soyad']
        dogum_tarihi = request.form['dogum_tarihi']
        cinsiyet = request.form['cinsiyet']
        telefon_numarasi = request.form['telefon_numarasi']
        adres = request.form['adres']

        yeni_hasta = Hasta(ad=ad, soyad=soyad, dogum_tarihi=dogum_tarihi, cinsiyet=cinsiyet, telefon_numarasi=telefon_numarasi, adres=adres)
        db.session.add(yeni_hasta)
        db.session.commit()
        flash('Hasta başarıyla eklendi!', 'success')
        return redirect(url_for('admin_hastalar'))

    return render_template('admin_hasta_ekle.html')

@app.route('/admin/hasta_guncelle/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_hasta_guncelle(id):
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    hasta = Hasta.query.get_or_404(id)
    if request.method == 'POST':
        hasta.ad = request.form['ad']
        hasta.soyad = request.form['soyad']
        hasta.dogum_tarihi = request.form['dogum_tarihi']
        hasta.cinsiyet = request.form['cinsiyet']
        hasta.telefon_numarasi = request.form['telefon_numarasi']
        hasta.adres = request.form['adres']

        db.session.commit()
        flash('Hasta bilgileri başarıyla güncellendi!', 'success')
        app.logger.info(f"Updated Hasta: {hasta}")
        return redirect(url_for('admin_hastalar'))

    return render_template('admin_hasta_guncelle.html', hasta=hasta)


@app.route('/admin/hasta_sil/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_hasta_sil(id):
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    hasta = Hasta.query.get_or_404(id)
    db.session.delete(hasta)
    db.session.commit()
    flash('Hasta başarıyla silindi!', 'success')
    return redirect(url_for('admin_hastalar'))

@app.route('/admin/doktorlar', methods=['GET', 'POST'])
@login_required
def admin_doktorlar():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    doktorlar = Doktor.query.all()
    return render_template('admin_doktorlar.html', doktorlar=doktorlar)

@app.route('/admin/doktor_ekle', methods=['GET', 'POST'])
@login_required
def admin_doktor_ekle():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        ad = request.form['ad']
        soyad = request.form['soyad']
        uzmanlik_alani = request.form['uzmanlik_alani']
        calistigi_hastane = request.form['calistigi_hastane']

        yeni_doktor = Doktor(ad=ad, soyad=soyad, uzmanlik_alani=uzmanlik_alani, calistigi_hastane=calistigi_hastane)
        db.session.add(yeni_doktor)
        db.session.commit()
        flash('Doktor başarıyla eklendi!', 'success')
        return redirect(url_for('admin_doktorlar'))

    return render_template('admin_doktor_ekle.html')

@app.route('/admin/doktor_guncelle/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_doktor_guncelle(id):
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    doktor = Doktor.query.get_or_404(id)
    if request.method == 'POST':
        doktor.ad = request.form['ad']
        doktor.soyad = request.form['soyad']
        doktor.uzmanlik_alani = request.form['uzmanlik_alani']
        doktor.calistigi_hastane = request.form['calistigi_hastane']

        db.session.commit()
        flash('Doktor bilgileri başarıyla güncellendi!', 'success')
        app.logger.info(f"Updated Doktor: {doktor}")
        return redirect(url_for('admin_doktorlar'))

    return render_template('admin_doktor_guncelle.html', doktor=doktor)


@app.route('/admin/doktor_sil/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_doktor_sil(id):
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    doktor = Doktor.query.get_or_404(id)
    aktif_randevular = Randevu.query.filter_by(doktor_id=doktor.id).count()
    if aktif_randevular > 0:
        flash('Aktif randevusu bulunan doktor silinemez!', 'danger')
        return redirect(url_for('admin_doktorlar'))

    db.session.delete(doktor)
    db.session.commit()
    flash('Doktor başarıyla silindi!', 'success')
    return redirect(url_for('admin_doktorlar'))

@app.route('/admin/randevular', methods=['GET', 'POST'])
@login_required
def admin_randevular():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    randevular = Randevu.query.all()
    return render_template('admin_randevular.html', randevular=randevular)

@app.route('/admin/randevu_ekle', methods=['GET', 'POST'])
@login_required
def admin_randevu_ekle():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    hastalar = Hasta.query.all()
    doktorlar = Doktor.query.all()

    if request.method == 'POST':
        hasta_id = request.form['hasta_id']
        doktor_id = request.form['doktor_id']
        randevu_tarihi = request.form['randevu_tarihi']
        randevu_saati = request.form['randevu_saati']

        yeni_randevu = Randevu(
            hasta_id=hasta_id,
            doktor_id=doktor_id,
            randevu_tarihi=randevu_tarihi,
            randevu_saati=randevu_saati
        )
        db.session.add(yeni_randevu)
        db.session.commit()
        flash('Randevu başarıyla eklendi!', 'success')
        return redirect(url_for('admin_randevular'))

    return render_template('admin_randevu_ekle.html', hastalar=hastalar, doktorlar=doktorlar)

@app.route('/admin/randevu_guncelle/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_randevu_guncelle(id):
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    randevu = Randevu.query.get_or_404(id)
    if request.method == 'POST':
        randevu.hasta_id = request.form['hasta_id']
        randevu.doktor_id = request.form['doktor_id']
        randevu.randevu_tarihi = request.form['randevu_tarihi']
        randevu.randevu_saati = request.form['randevu_saati']

        db.session.commit()
        flash('Randevu bilgileri başarıyla güncellendi!', 'success')
        app.logger.info(f"Updated Randevu: {randevu}")
        return redirect(url_for('admin_randevular'))

    return render_template('admin_randevu_guncelle.html', randevu=randevu)

@app.route('/admin/randevu_sil/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_randevu_sil(id):
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    randevu = Randevu.query.get_or_404(id)
    db.session.delete(randevu)
    db.session.commit()
    flash('Randevu başarıyla silindi!', 'success')
    return redirect(url_for('admin_randevular'))

@app.route('/admin/tibbi_raporlar', methods=['GET', 'POST'])
@login_required
def admin_tibbi_raporlar():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    tibbi_raporlar = TibbiRapor.query.all()
    return render_template('admin_tibbi_raporlar.html', tibbi_raporlar=tibbi_raporlar)

@app.route('/admin/tibbi_rapor_ekle', methods=['GET', 'POST'])
@login_required
def admin_tibbi_rapor_ekle():
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    hastalar = Hasta.query.all()
    doktorlar = Doktor.query.all()

    if request.method == 'POST':
        hasta_id = request.form['hasta_id']
        doktor_id = request.form['doktor_id']
        rapor_tarihi = request.form['rapor_tarihi']
        rapor_icerigi = request.form['rapor_icerigi']

        yeni_rapor = TibbiRapor(
            hasta_id=hasta_id,
            doktor_id=doktor_id,
            rapor_tarihi=rapor_tarihi,
            rapor_icerigi=rapor_icerigi
        )
        db.session.add(yeni_rapor)
        db.session.commit()
        flash('Tıbbi rapor başarıyla eklendi!', 'success')
        return redirect(url_for('admin_tibbi_raporlar'))

    return render_template('admin_tibbi_rapor_ekle.html', hastalar=hastalar, doktorlar=doktorlar)

@app.route('/admin/tibbi_rapor_guncelle/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_tibbi_rapor_guncelle(id):
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    tibbi_rapor = TibbiRapor.query.get_or_404(id)
    if request.method == 'POST':
        tibbi_rapor.hasta_id = request.form['hasta_id']
        tibbi_rapor.doktor_id = request.form['doktor_id']
        tibbi_rapor.rapor_tarihi = request.form['rapor_tarihi']
        tibbi_rapor.rapor_icerigi = request.form['rapor_icerigi']

        db.session.commit()
        flash('Tıbbi rapor bilgileri başarıyla güncellendi!', 'success')
        app.logger.info(f"Updated Tibbi Rapor: {tibbi_rapor}")
        return redirect(url_for('admin_tibbi_raporlar'))

    return render_template('admin_tibbi_rapor_guncelle.html', tibbi_rapor=tibbi_rapor)


@app.route('/admin/tibbi_rapor_sil/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_tibbi_rapor_sil(id):
    if current_user.role != 'yonetici':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    tibbi_rapor = TibbiRapor.query.get_or_404(id)
    db.session.delete(tibbi_rapor)
    db.session.commit()
    flash('Tıbbi rapor başarıyla silindi!', 'success')
    return redirect(url_for('admin_tibbi_raporlar'))

@app.route('/randevu_olustur', methods=['GET', 'POST'])
@login_required
def randevu_olustur():
    if current_user.role != 'hasta':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    doktorlar = Doktor.query.all()

    if request.method == 'POST':
        doktor_id = request.form.get('doktor_id')
        randevu_tarihi = request.form.get('randevu_tarihi')
        randevu_saati = request.form.get('randevu_saati')

        if not doktor_id or not randevu_tarihi or not randevu_saati:
            flash('Lütfen tüm alanları doldurunuz.', 'danger')
            return render_template('randevu_olustur.html', doktorlar=doktorlar)

        yeni_randevu = Randevu(
            hasta_id=current_user.id,
            doktor_id=doktor_id,
            randevu_tarihi=randevu_tarihi,
            randevu_saati=randevu_saati
        )
        db.session.add(yeni_randevu)
        db.session.commit()
        flash('Randevu başarıyla oluşturuldu!', 'success')
        return redirect(url_for('hasta_home'))

    return render_template('randevu_olustur.html', doktorlar=doktorlar)

@app.route('/tibbi_rapor_ekle/<int:randevu_id>', methods=['GET', 'POST'])
@login_required
def tibbi_rapor_ekle(randevu_id):
    if current_user.role != 'doktor':
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('index'))

    randevu = Randevu.query.get_or_404(randevu_id)
    if request.method == 'POST':
        rapor_icerigi = request.form.get('rapor_icerigi')

        if not rapor_icerigi:
            flash('Lütfen rapor içeriğini girin.', 'danger')
            return render_template('tibbi_rapor_ekle.html', randevu=randevu)

        yeni_rapor = TibbiRapor(
            hasta_id=randevu.hasta_id,
            doktor_id=current_user.id,
            rapor_tarihi=datetime.date.today(),
            rapor_icerigi=rapor_icerigi
        )
        db.session.add(yeni_rapor)
        db.session.commit()
        flash('Tıbbi rapor başarıyla eklendi!', 'success')
        return redirect(url_for('doktor_home'))

    return render_template('tibbi_rapor_ekle.html', randevu=randevu)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
