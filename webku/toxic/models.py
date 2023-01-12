from django.db import models

# Create your models here.
class rekapitulasi(models.Model):
    id_rekaps = models.BigAutoField(primary_key=True)
    link_yt = models.CharField(max_length=100)
    nama_video = models.CharField(max_length=100)
    hasil_transkripsi = models.TextField()
    hasil_deteksi = models.TextField()
    klasifikasi = models.CharField(max_length=1)
    tanggal = models.DateTimeField()

    objects = models.Manager()

class kasar(models.Model):
    id_kasar = models.BigAutoField(primary_key=True)
    kata_kasar = models.CharField(max_length=20)
    label = models.CharField(max_length=10)
    
    objects = models.Manager()

class saran(models.Model):
    id_saran = models.BigAutoField(primary_key=True)
    saran_kata = models.CharField(max_length=20)
    label = models.CharField(max_length=10)
    
    objects = models.Manager()