from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Hasta(db.Model):
    __tablename__ = 'hastalar'
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    dogum_tarihi = db.Column(db.Date, nullable=False)
    cinsiyet = db.Column(db.String(10))
    telefon_numarasi = db.Column(db.String(15))
    adres = db.Column(db.Text)

class Doktor(db.Model):
    __tablename__ = 'doktorlar'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    uzmanlik_alani = db.Column(db.String(100))
    calistigi_hastane = db.Column(db.String(100))


class Yonetici(db.Model):
    __tablename__ = 'yoneticiler'
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)

class Randevu(db.Model):
    __tablename__ = 'randevular'
    id = db.Column(db.Integer, primary_key=True)
    hasta_id = db.Column(db.Integer, db.ForeignKey('hastalar.id'), nullable=False)
    doktor_id = db.Column(db.Integer, db.ForeignKey('doktorlar.id'), nullable=False)
    randevu_tarihi = db.Column(db.Date, nullable=False)
    randevu_saati = db.Column(db.Time, nullable=False)
    hasta = db.relationship('Hasta', backref=db.backref('randevular', lazy=True))
    doktor = db.relationship('Doktor', backref=db.backref('randevular', lazy=True))

class TibbiRapor(db.Model):
    __tablename__ = 'tibbi_raporlar'
    id = db.Column(db.Integer, primary_key=True)
    hasta_id = db.Column(db.Integer, db.ForeignKey('hastalar.id'), nullable=False)
    doktor_id = db.Column(db.Integer, db.ForeignKey('doktorlar.id'))
    yonetici_id = db.Column(db.Integer, db.ForeignKey('yoneticiler.id'))
    rapor_tarihi = db.Column(db.Date, nullable=False)
    rapor_icerigi = db.Column(db.Text)
    resim_url = db.Column(db.Text)
    json_veri = db.Column(db.JSON)
    hasta = db.relationship('Hasta', backref=db.backref('tibbi_raporlar', lazy=True))
    doktor = db.relationship('Doktor', backref=db.backref('tibbi_raporlar', lazy=True))
    yonetici = db.relationship('Yonetici', backref=db.backref('tibbi_raporlar', lazy=True))
